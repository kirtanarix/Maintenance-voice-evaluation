"""Evidence-only asset reference ingestion. Standard library; no model/API calls.

Run: python3 -B src/run_dictionary_v2_phase1.py
Outputs are exclusive-create: an existing output directory is never overwritten.
XLSX numbers remain their exact XML numeric text (value_type=number), with styles
and workbook date system retained. Formulas are retained, never evaluated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile, is_zipfile

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("Live Company", "Demo Company")
KINDS = ("asset", "asset_metadata", "identifier_mapping", "workflow",
         "personnel_or_status", "guidance", "footer_or_summary", "unresolved")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PLACEHOLDERS = {"", "na", "n/a", "n.a.", "not available", "not applicable",
                "nil", "nill", "none", "-", "--na--", "default manufacturer",
                "default fabrication"}
NAMES = {"asset name", "name", "item name", "item name (asset name example)",
         "type of vehicle", "description"}
IDS = {"asset tag": "asset_tag", "cust tag id": "customer_tag",
       "kc asset tag": "customer_tag", "serial": "serial_number",
       "serial number": "serial_number", "manufacturer serial no.": "manufacturer_serial",
       "manufserialno.": "manufacturer_serial", "vehicle number": "vehicle_registration",
       "sap equipment no.": "equipment_number", "sap equipment number (balco)": "equipment_number",
       "equipment": "equipment_number", "equipment code": "equipment_code",
       "tech identification number": "technical_id", "techidentno.": "technical_id"}
# These terms are evidence for a physical object, not a canonical vocabulary.
PHYSICAL = re.compile(
    r"\b(pump|submercibal|excavator|extinguisher|extingusher|extenguisher|fire ext|"
    r"ac unit|air condition\w*|conveyor|motor|compressor|blower|fan|valve|gate|"
    r"furnace|crane|mill|kiln|cooler|heater|boiler|burner|tank|silo|hopper|"
    r"filter|bagfilter|baghouse|separator|seperator|cyclone|cylone|feeder|"
    r"gear ?box|coupling|bearing|belt|chain|shaft|pulley|roller|dryer|"
    r"switch\w*|panel|transformer|mcc|plc|rheostat|capacitor|breaker|"
    r"sensor|detector|gauge|transmitter|meter|flowmeter|analy[sz]er|"
    r"computer|desktop|laptop|printer|scanner|monitor|keyboard|camera|cctv|"
    r"server|router|modem|ups|battery|lighting|light|lamp|dg set|generator|"
    r"machine|loom|vehicle|truck|tipper|pickup|pick up|compactor|dumper|"
    r"loader|dozer|grader|drill|tanker|forklift|fork lift|tyre|engine|"
    r"hose|hydrant|reel|bucket|door|scba|shower|kit|box|papr|lel|vesda|"
    r"chair|cylinder|concentrator|mask|fire ball|flooding system|"
    r"rack|desk|table|cabinet|furniture|freezer|chiller|refrigerator|"
    r"scrubber|reactor|vessel|autoclave|centrifuge|weigh\w*|scale|"
    r"air slide|airlock|air lock|damper|duct\w*|chimney|stack|"
    r"reclaimer|stacker|sampler|elevator|lift|hoist|precalciner|"
    r"rock breaker|loading|spout|bin|sump|screen|crusher|screw|"
    r"flow element|pig barrel|skid|rtu|rtd|tr unit|earth pit|"
    r"ground bed|insulating joint|odorizer|epabx|pipeline|"
    r"fire fighting system|detection system|robot|robo|building|"
    r"air handling unit|ahu|water dispenser|ro plant|purifier|"
    r"tending assembly|press|turbine|economizer|heat exchanger)\b", re.I)


def packed(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def stable(prefix, *parts):
    return prefix + "_" + hashlib.sha256(packed(parts).encode()).hexdigest()[:24]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm(value):
    return " ".join(str(value or "").split()).casefold()


def valid(value):
    return value is not None and norm(value) not in PLACEHOLDERS


def cell(value, kind="string", **extra):
    return {"value_raw": value, "value_type": kind, **extra}


def text_content(node):
    # Only text/rich-text runs: do not accidentally append phonetic annotations.
    return "".join(t.text or "" for t in node.findall("m:t", NS) + node.findall("m:r/m:t", NS))


def col_number(address):
    result = 0
    for char in re.match(r"[A-Z]+", address).group():
        result = result * 26 + ord(char) - 64
    return result


def xlsx_tables(path):
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships}
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [text_content(s) for s in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        styles = []
        formats = {}
        if "xl/styles.xml" in archive.namelist():
            style_xml = ET.fromstring(archive.read("xl/styles.xml"))
            formats = {n.attrib["numFmtId"]: n.attrib["formatCode"]
                       for n in style_xml.findall("m:numFmts/m:numFmt", NS)}
            styles = [dict(n.attrib) for n in style_xml.findall("m:cellXfs/m:xf", NS)]
        props = workbook.find("m:workbookPr", NS)
        metadata = {"date_system": "1904" if props is not None and props.get("date1904") in ("1", "true") else "1900",
                    "cell_styles": styles, "custom_number_formats": formats,
                    "numeric_representation": "Exact OOXML numeric text; dates retain serial plus style, not reformatted dates."}
        tables = []
        for sheet in workbook.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[REL]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            xml = ET.fromstring(archive.read(target))
            rows = []
            for row in xml.findall("m:sheetData/m:row", NS):
                values = {}
                for c in row.findall("m:c", NS):
                    index = col_number(c.attrib["r"])
                    value = c.find("m:v", NS)
                    raw = value.text if value is not None else None
                    typ = c.get("t", "n")
                    if typ == "s":
                        raw, kind = strings[int(raw)], "string"
                    elif typ == "inlineStr":
                        inline = c.find("m:is", NS)
                        raw, kind = text_content(inline) if inline is not None else "", "string"
                    else:
                        kind = {"n": "number", "b": "boolean", "e": "error", "d": "date", "str": "string"}.get(typ, typ)
                        if raw is None:
                            kind = "null"
                    extra = {"cell_present": True, "style_index": int(c.get("s", "0"))}
                    formula = c.find("m:f", NS)
                    if formula is not None:
                        extra.update(cached_value_raw=raw, cached_value_type=kind,
                                     formula_attributes=dict(formula.attrib))
                        raw, kind = "=" + (formula.text or ""), "formula"
                    values[index] = cell(raw, kind, **extra)
                rows.append({"number": int(row.attrib["r"]), "values": values,
                             "width": max(values, default=0), "row_attributes": dict(row.attrib)})
            tables.append({"name": sheet.attrib["name"], "rows": rows,
                           "state": sheet.get("state", "visible"),
                           "merged_ranges": [n.attrib["ref"] for n in xml.findall("m:mergeCells/m:mergeCell", NS)]})
        return tables, metadata


class HTMLTables(HTMLParser):
    """Text observations plus original cell markup; preserve span coordinates."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.table, self.row, self.current = [], None, None, None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth > 1:
                raise ValueError("Nested HTML tables require manual parsing")
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.current = {"text": "", "markup": self.get_starttag_text(), "attrs": dict(attrs)}
        elif self.current is not None:
            self.current["markup"] += self.get_starttag_text()
            if tag == "br":
                self.current["text"] += "\n"

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data
            self.current["markup"] += data

    def handle_endtag(self, tag):
        if self.current is not None:
            self.current["markup"] += "</" + tag + ">"
        if tag in ("td", "th") and self.current is not None:
            self.row.append(self.current)
            self.current = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table":
            self.tables.append(self.table)
            self.table = None
            self.depth -= 1


def read_text(path):
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "cp1252"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("Cannot decode source with UTF-8/BOM, UTF-16 BOM or CP1252")


def parse(path):
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls") and is_zipfile(path):
        tables, meta = xlsx_tables(path)
        return "xlsx", tables, meta
    if suffix == ".csv":
        text, encoding = read_text(path)
        rows, previous = [], 0
        lines = text.splitlines(keepends=True)
        warnings = []
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        while True:
            issue = None
            try:
                values = next(reader)
            except StopIteration:
                break
            except csv.Error as exc:
                if str(exc) != "unexpected end of data":
                    raise
                # Recover only the incomplete final observation, never silently
                # treat it as a valid asset. Keep its exact decoded CSV fragment.
                fragment = "".join(lines[previous:])
                recovered = list(csv.reader(io.StringIO(fragment, newline="")))
                if len(recovered) != 1:
                    raise ValueError("Cannot safely isolate malformed CSV tail") from exc
                values = recovered[0]
                issue = f"Unterminated quoted CSV field at EOF, logical row {len(rows) + 1}; recovered fields are provisional"
                warnings.append(issue)
            rows.append({"number": len(rows) + 1, "width": len(values),
                         "values": {j: cell(v) for j, v in enumerate(values, 1)},
                         "physical_line_start": previous + 1, "physical_line_end": reader.line_num})
            if issue:
                rows[-1].update(parse_issue=issue, raw_record_text=fragment)
                break
            previous = reader.line_num
        return "csv", [{"name": None, "rows": rows}], {"encoding": encoding, "delimiter": ",", "parse_warnings": warnings}
    if suffix in (".xls", ".html", ".htm"):
        if path.read_bytes()[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
            raise NotImplementedError("Binary XLS/BIFF is unsupported; no conversion or source modification attempted")
        text, encoding = read_text(path)
        parser = HTMLTables()
        parser.feed(text)
        if not parser.tables:
            raise ValueError("No HTML tables found")
        tables = []
        for ti, table in enumerate(parser.tables, 1):
            rows, occupied = [], {}
            for ri, raw_row in enumerate(table, 1):
                values, index = {}, 1
                for raw in raw_row:
                    while occupied.get(index, 0) >= ri:
                        index += 1
                    span = int(raw["attrs"].get("colspan", "1"))
                    height = int(raw["attrs"].get("rowspan", "1"))
                    values[index] = cell(raw["text"], html_markup=raw["markup"],
                                         html_attributes=raw["attrs"], colspan=span, rowspan=height)
                    for col in range(index, index + span):
                        occupied[col] = ri + height - 1
                    index += span
                rows.append({"number": ri, "width": index - 1, "values": values})
            tables.append({"name": "HTML table " + str(ti), "rows": rows})
        return "html_table", tables, {"encoding": encoding, "html_note": "value_raw is decoded text; markup retains tags and decoded text, original bytes remain in source."}
    raise NotImplementedError(f"Unsupported {suffix or 'extensionless'} source: row/table ingestion not implemented")


def header_index(table):
    for i, row in enumerate(table["rows"][:20]):
        labels = {norm(v["value_raw"]) for v in row["values"].values()}
        if (labels & {"asset tag", "vehicle number", "equipment"}
                or {"section", "parameters", "frequency"} <= labels):
            return i
    return None


def raw_cells(row, headers):
    return [{"column_index": i,
             "header_raw": headers.get(i, {}).get("value_raw") or None,
             **row["values"].get(i, cell(None, "null", cell_present=False))}
            for i in range(1, max(row["width"], max(headers, default=0)) + 1)]


def fields(cells):
    return [(norm(c["header_raw"]), c["value_raw"], c["column_index"]) for c in cells if valid(c["value_raw"])]


def classify(cells, preamble=False, has_header=True):
    values = fields(cells)
    texts = [norm(c["value_raw"]) for c in cells if c["value_raw"] is not None]
    labels = {norm(c["header_raw"]) for c in cells if c["header_raw"]}
    if not any(texts):
        return "unresolved", "Explicit blank source row; retained without inventing an asset"
    if preamble:
        return "guidance", "Preamble before detected tabular header"
    if any(t in ("mandatory fields", "not mandatory") for t in texts):
        return "guidance", "Explicit field-guidance label"
    if any("the following is an example" in t for t in texts):
        return "guidance", "Source explicitly labels this record as an example"
    if any(t in ("on medical leave", "on m/l") for t in texts):
        return "personnel_or_status", "Explicit staff leave/status label"
    if not has_header:
        return "unresolved", "No supported header identified; positional observations retained"
    names = [str(v) for h, v, _ in values if h in NAMES and (h != "description" or "equipment" in labels)]
    combined = " ".join(names)
    categories = " ".join(str(v) for h, v, _ in values if h == "category")
    if {"parameters", "frequency"} <= labels:
        return "workflow", "Maintenance checklist parameters and frequency; not individual equipment records"
    if re.search(r"\b(fabrication request|workflow|incident report|daily lock opening|daily lock closing)\b", combined, re.I):
        return "workflow", "Explicit request/report/workflow or operating-process label"
    if not names and {"asset tag", "cust tag id"} <= labels:
        return "identifier_mapping", "Explicit asset-tag/customer-tag crosswalk without asset name"
    if not names and any(h == "asset tag" for h, _, _ in values):
        return "asset_metadata", "Tagged metadata without equipment description"
    nonempty = [c for c in cells if valid(c["value_raw"])]
    if not names and nonempty and all(norm(c["header_raw"]) in {"purchase cost", "cost", "total"} for c in nonempty):
        return "footer_or_summary", "Only total/cost columns are populated, without an asset identity"
    if re.search(r"\b(testing|test\d*|maintenance|process|inspection)\b", combined, re.I):
        return "unresolved", "Test/maintenance/process label may not describe a physical asset"
    if re.search(r"\b(temperature|winding temp|bearing temp)\b", combined, re.I) and not re.search(r"\b(sensor|switch|gauge|transmitter)\b", combined, re.I):
        return "unresolved", "Measurement/monitoring label; physical asset identity is unclear"
    match = PHYSICAL.search(combined) or (PHYSICAL.search(categories) if names else None)
    if names and match:
        return "asset", f"Source name/category contains physical-equipment term: {match.group(0)}"
    return "unresolved", "Insufficient explicit physical-equipment or other record-kind evidence"


def industry_evidence(filename, cells):
    explicit = [(v, i) for h, v, i in fields(cells) if h in {"industry", "industry name"}]
    if explicit:
        distinct = sorted({str(v) for v, _ in explicit})
        return {"industry": distinct[0] if len(distinct) == 1 else None,
                "status": "confirmed" if len(distinct) == 1 else "ambiguous",
                "evidence": [{"field": "industry", "value_raw": v, "column_index": i} for v, i in explicit]}
    for term in ("cement", "dairy", "refinery", "printing"):
        if term in filename.casefold():
            return {"industry": term, "status": "confirmed", "evidence": [{"filename": filename, "basis": "Explicit filename label; not a verified company-wide taxonomy"}]}
    if any(t in filename.casefold() for t in ("hvac", "fire safety", "gas&mix", "garbage collect")):
        return {"industry": None, "status": "ambiguous", "evidence": [{"filename": filename, "basis": "Domain/service context retained; no industry assignment"}]}
    return {"industry": None, "status": "unknown", "evidence": []}


def make_record(source, table, row, headers, preamble=False, has_header=True):
    cells = raw_cells(row, headers)
    kind, reason = classify(cells, preamble, has_header)
    if row.get("parse_issue"):
        kind, reason = "unresolved", row["parse_issue"]
    evidence = industry_evidence(source["filename"], cells)
    names, identifiers, manufacturers, models, types, companies, locations = [], [], [], [], [], [], []
    for h, v, i in fields(cells):
        observation = {"column_index": i, "value_raw": v, "value_normalized": norm(v)}
        if h in NAMES and (h != "description" or i == 2):
            names.append(observation)
        if h in IDS:
            identifiers.append({"namespace": IDS[h], **observation})
        if h == "manufacturer":
            manufacturers.append(observation)
        if h in {"model", "model name", "model number", "model no."}:
            models.append(observation)
        if h in {"type and capacity of fire extinguisher", "category"}:
            types.append(observation)
        if h in {"company", "company code"}:
            companies.append(observation)
        if h in {"location", "location name", "functional loc."}:
            locations.append(observation)
    rid = stable("record", source["source_id"], table["name"], row["number"])
    record = {"record_id": rid, "source_id": source["source_id"],
              "source_group": source["company_source_group"], "filename": source["filename"],
              "sheet": table["name"], "row_number": row["number"],
              "source_column_count": row["width"], "record_kind": kind,
              "classification_reason": reason, "raw_cells": cells,
              "derived": {"asset_name_candidates": names, "identifiers": identifiers,
                          "manufacturer_observations": manufacturers, "model_observations": models,
                          "type_observations": types, "company_observations": companies,
                          "location_observations": locations, "industry": evidence["industry"],
                          "industry_evidence": evidence}}
    for key in ("physical_line_start", "physical_line_end", "row_attributes", "parse_issue", "raw_record_text"):
        if key in row:
            record[key] = row[key]
    return record


def source_records(source, tables):
    for table in tables:
        hi = header_index(table)
        headers = table["rows"][hi]["values"] if hi is not None else {}
        for i, row in enumerate(table["rows"]):
            if i != hi:
                yield make_record(source, table, row, headers, hi is not None and i < hi, hi is not None)


def sheet_inventory(table):
    hi = header_index(table)
    header = table["rows"][hi] if hi is not None else None
    rows = table["rows"]
    labels = Counter(norm(c["value_raw"]) for c in (header["values"].values() if header else []) if c["value_raw"])
    return {"sheet": table["name"], "state": table.get("state"),
            "header_row_number": header["number"] if header else None,
            "header_cells": raw_cells(header, {}) if header else [],
            "source_row_count": len(rows), "record_count": len(rows) - (header is not None),
            "blank_record_count": sum(not any(c["value_raw"] not in (None, "") for c in r["values"].values()) for r in rows),
            "duplicate_headers": [k for k, n in labels.items() if n > 1],
            "row_width_counts": {str(k): v for k, v in Counter(r["width"] for r in rows).items()},
            "row_number_gaps": [list(pair) for pair in zip([0] + [r["number"] for r in rows], [r["number"] for r in rows]) if pair[1] - pair[0] > 1],
            "merged_ranges": table.get("merged_ranges", [])}


class CandidateIndex:
    def __init__(self):
        self.indices = defaultdict(lambda: defaultdict(set))
        self.info = {}

    def add(self, record):
        rid, d = record["record_id"], record["derived"]
        group = record["source_group"]
        company = tuple(str(c["value_raw"]) for c in d["company_observations"]) or (record["source_id"],)
        signature = tuple(tuple(str(o["value_raw"]) for o in d[field]) for field in ("asset_name_candidates", "model_observations", "location_observations"))
        self.info[rid] = (record["source_id"], signature)
        if record.get("parse_issue"):
            return
        raw = [(c["column_index"], c["header_raw"], c["value_raw"], c["value_type"])
               for c in record["raw_cells"]]
        if any(valid(c["value_raw"]) for c in record["raw_cells"]):
            self.indices["exact"][(group, stable("raw", raw))].add(rid)
        if record["record_kind"] not in {"asset", "asset_metadata", "identifier_mapping", "unresolved", "workflow"}:
            return
        for field in ("asset_name_candidates", "manufacturer_observations", "model_observations", "type_observations"):
            for obs in d[field]:
                value = str(obs["value_raw"])
                scope = (group, field)
                if field == "asset_name_candidates":
                    self.indices["name"][(group, company, value)].add(rid)
                for typ, key in (("case", value.casefold()), ("whitespace", " ".join(value.split())),
                                 ("punctuation", re.sub(r"[^\w\s]", "", value))):
                    self.indices[typ][(*scope, key, value)].add(rid)
        for obs in d["identifiers"]:
            # Comparison is exact: no case, punctuation or leading-zero changes.
            namespace, value = obs["namespace"], str(obs["value_raw"])
            self.indices["identifier"][(group, company, namespace, value)].add(rid)
            if namespace in {"equipment_number", "asset_tag", "manufacturer_serial"}:
                self.indices["cross_file"][(group, namespace, value)].add(rid)

    def candidates(self):
        result = []
        def emit(kind, ids, reason, evidence):
            ids = sorted(ids)
            if len(ids) < 2:
                return
            result.append({"candidate_id": stable("candidate", kind, evidence, ids),
                           "record_ids": ids, "candidate_type": kind, "reason": reason,
                           "evidence": evidence, "status": "needs_review"})
        for typ in ("exact", "name", "identifier", "cross_file"):
            for key, ids in sorted(self.indices[typ].items(), key=lambda kv: packed(kv[0])):
                if len(ids) < 2:
                    continue
                if typ == "exact":
                    emit("possible_duplicate", ids, "Equal positional headers, raw values and types; repeated observations remain separate", {"basis": "exact_source_record"})
                elif typ == "name":
                    emit("repeated_asset_name", ids, "Exact name repeats; this does not imply the same physical asset", {"basis": "exact_asset_name", "source_group": key[0]})
                elif typ == "identifier":
                    signatures = [self.info[rid][1] for rid in ids]
                    conflict = any(len({sig[i] for sig in signatures if sig[i]}) > 1 for i in range(3))
                    emit("conflicting_identifier" if conflict else "repeated_identifier", ids,
                         "Exact identifier repeats within raw company/source scope" + (" with different name, model or location observations" if conflict else ""),
                         {"namespace": key[2], "value_raw": key[3], "scope": list(key[1])})
                elif len({self.info[rid][0] for rid in ids}) > 1:
                    emit("possible_same_instance", ids, "Exact identifier occurs in multiple files; company equivalence and instance identity are NOT resolved",
                         {"namespace": key[1], "value_raw": key[2], "source_group": key[0]})
        for typ in ("case", "whitespace", "punctuation"):
            groups = defaultdict(dict)
            for key, ids in self.indices[typ].items():
                groups[key[:-1]][key[-1]] = ids
            for key, variants in sorted(groups.items(), key=lambda kv: packed(kv[0])):
                if len(variants) > 1:
                    emit("possible_alias", set().union(*variants.values()),
                         f"{typ}-only variation in {key[1]}; no alias or equivalence asserted",
                         {"variation": typ, "field": key[1], "values_raw": sorted(variants), "source_group": key[0]})
        return sorted(result, key=lambda c: c["candidate_id"])


def discover(input_root):
    found = []
    for group in GROUPS:
        directory = input_root / group
        if not directory.is_dir():
            raise ValueError(f"Missing required source group: {directory}")
        found.extend((group, p) for p in sorted(directory.rglob("*")) if p.is_file())
    return found


def validate(input_root, inventory, records_path, candidates, original_hashes):
    """Re-read source bytes and output lines: compare every record and raw cell."""
    checks = {}
    discovered = discover(input_root)
    checks["all_discovered_files_in_inventory"] = {str(p.relative_to(input_root)) for _, p in discovered} == {s["relative_path"] for s in inventory["sources"]}
    checks["source_bytes_unchanged"] = all(sha(p) == original_hashes[str(p)] for _, p in discovered)
    seen, counts = set(), Counter()
    parsed_count = 0
    with records_path.open(encoding="utf-8") as stream:
        for source in inventory["sources"]:
            if source["parsing_status"] != "parsed":
                continue
            _, tables, _ = parse(input_root / source["relative_path"])
            for expected in source_records(source, tables):
                line = stream.readline()
                if not line:
                    raise ValueError("Validation: missing output record")
                actual = json.loads(line)
                if actual != expected:
                    raise ValueError(f"Validation: source/output mismatch at {expected['record_id']}")
                if actual["record_id"] in seen or actual["record_kind"] not in KINDS:
                    raise ValueError("Validation: duplicate record ID or invalid kind")
                seen.add(actual["record_id"])
                counts[source["source_id"]] += 1
                parsed_count += 1
        if stream.readline():
            raise ValueError("Validation: unexpected extra output record")
    checks["every_parsed_row_exactly_once"] = parsed_count == sum(s["record_count"] for s in inventory["sources"])
    checks["per_source_counts_reconcile"] = all(counts[s["source_id"]] == s["record_count"] for s in inventory["sources"])
    checks["raw_values_headers_positions_and_unnamed_cells_preserved"] = True
    checks["every_record_has_valid_kind"] = True
    checks["groups_preserved"] = all(s["company_source_group"] in GROUPS and s["relative_path"].split("/")[0] == s["company_source_group"] for s in inventory["sources"])
    checks["all_candidates_unresolved_and_referentially_valid"] = all(c["status"] == "needs_review" and len(c["record_ids"]) >= 2 and set(c["record_ids"]) <= seen for c in candidates)
    checks["candidate_ids_unique"] = len({c["candidate_id"] for c in candidates}) == len(candidates)
    checks["no_canonical_merge"] = checks["every_parsed_row_exactly_once"] and checks["all_candidates_unresolved_and_referentially_valid"]
    checks["source_hashes_still_unchanged_after_validation"] = all(sha(p) == original_hashes[str(p)] for _, p in discovered)
    return {"passed": all(checks.values()), "checks": checks,
            "method": "Second source parse compared to every serialized record; source SHA-256 checked before/after; candidate references and coverage reconciled."}


def write_json(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def report(inventory, candidates):
    sources = inventory["sources"]
    counts = Counter(c["candidate_type"] for c in candidates)
    good = sum(s["parsing_status"] == "parsed" for s in sources)
    lines = ["# Asset Reference — Phase 1 Report", "", "Phase 1 does not perform canonical asset merging.", "",
             f"Validation: **{'PASS' if inventory['validation']['passed'] else 'FAIL'}**. Ingestion coverage: **{good}/{len(sources)} files parsed**.",
             "Unsupported/failed files remain inventoried with zero ingested records; validation PASS covers supported-source preservation, not full-format coverage.", "",
             "## 1. Files discovered", "", "| Group | Filename | Format | Status | Records |", "|---|---|---|---|---:|"]
    for s in sources:
        lines.append(f"| {s['company_source_group']} | {s['filename'].replace('|', '&#124;')} | {s['file_type']} | {s['parsing_status']} | {s['record_count']} |")
    lines += ["", "## 2. Files successfully parsed", "", str(good), "", "## 3. Files that failed or are unsupported", ""]
    lines += [f"- {s['relative_path']}: {s.get('error')}" for s in sources if s["parsing_status"] != "parsed"] or ["None."]
    lines += ["", "## 4. Sheets discovered", "", f"Workbook sheets: {sum(len(s['sheet_names']) for s in sources)}. Empty sheets are included in the inventory.",
              "CSV uses sheet=null; HTML tables retain separate numbered table names.", "", "## 5. Total source records", "", str(sum(s["record_count"] for s in sources)),
              "", "Headers are retained as positional inventory cells. Every explicit row after the header and every preamble row becomes one record, including explicit blank rows. Missing XML row numbers are inventoried as gaps, not invented records. Counts therefore differ from nonempty-only exploration counts.",
              "", "## 6. Records by source group", ""]
    for group, summary in inventory["source_groups"].items():
        lines.append(f"- {group}: {summary['record_count']} records, {summary['file_count']} files.")
    lines += ["", "## 7. Records by record_kind", "", "| Kind | Live Company | Demo Company | Total |", "|---|---:|---:|---:|"]
    for kind in KINDS:
        values = [inventory["source_groups"][g]["record_kinds"].get(kind, 0) for g in GROUPS]
        lines.append(f"| {kind} | {values[0]} | {values[1]} | {sum(values)} |")
    lines += ["", "## 8. Candidate duplicate/alias counts", "", f"{len(candidates)} unresolved candidate groups; group counts are not pair counts or a duplicate-asset count."]
    lines += [f"- {kind}: {count}" for kind, count in sorted(counts.items())]
    lines += ["", "Case, whitespace and punctuation comparisons apply to derived lexical observations only. Identifiers are compared exactly. Placeholder values do not generate identifier candidates. No spelling correction, fuzzy alias resolution, company equivalence or instance merging is performed.",
              "", "## 9. Identifier conflicts", "", f"{counts['conflicting_identifier']} candidate groups with an exact scoped identifier but different name/model/location evidence.",
              "Same identifiers may denote legitimate revisions, metadata links or collisions; every candidate remains needs_review.", ""]
    for c in [c for c in candidates if c["candidate_type"] == "conflicting_identifier"][:12]:
        lines.append(f"- {c['candidate_id']}: {c['evidence']['namespace']}, {len(c['record_ids'])} observations. See candidate JSON for identifiers and record references.")
    lines += ["", "## 10. Industry evidence counts", ""]
    for group in GROUPS:
        lines.append(f"- {group}: {packed(inventory['source_groups'][group]['industry_evidence_counts'])}")
    lines += ["", "Confirmed means explicit source labeling, not independently verified sector membership. HVAC/fire-safety/service context is retained as ambiguous with industry=null. No generic/cross-industry parent is created.",
              "", "## 11. Unresolved records", ""]
    for group in GROUPS:
        lines.append(f"- {group}: {inventory['source_groups'][group]['record_kinds'].get('unresolved', 0)}. Reasons and source coordinates are on each JSONL record.")
    lines += ["", "## 12. Important warnings", ""]
    for s in sources:
        for warning in s["warnings"]:
            lines.append(f"- {s['filename']}: {warning}")
    lines += ["- Original identifiers, manufacturer/model spellings, company names and repeated records remain unchanged.",
              "- XLSX numbers are exact XML numeric strings tagged number; date serials retain style indexes and workbook date system. Formulas retain formula attributes/cached values and are never calculated. Shared/merged cells are not forward-filled.",
              "- Raw records retain administrative/personnel fields and any source credentials. Report summaries do not reproduce them; do not feed this full registry to extraction prompts indiscriminately.",
              "- Asset classification is conservative rule-based triage, not certification of a physical asset or final canonical identity.",
              "", "## 13. Coverage validation", ""]
    lines += [f"- {'PASS' if passed else 'FAIL'}: {name}" for name, passed in inventory["validation"].get("checks", {}).items()]
    if inventory["validation"].get("error"):
        lines.append("- ERROR: " + inventory["validation"]["error"])
    lines += ["", "## Reproduce", "", "`python3 -B src/run_dictionary_v2_phase1.py`", "",
              "Requires Python 3.10+ standard library only. Existing output directories are refused; use --output-dir with a new review directory for a subsequent run. Source files and existing extraction/evaluation/dictionary code are not written.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=ROOT / "inputs/dictionary_v2")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/dictionary_v2/phase1")
    args = parser.parse_args()
    input_root, output = args.input_root.resolve(), args.output_dir.resolve()
    if input_root == output or input_root in output.parents:
        parser.error("Output must be outside the protected input tree")
    found = discover(input_root)
    hashes = {str(p): sha(p) for _, p in found}
    output.mkdir(parents=True, exist_ok=False)
    inventory = {"schema_version": "phase1.1", "generated_at": datetime.now(timezone.utc).isoformat(),
                 "source_groups": {}, "sources": [], "canonical_merging_performed": False}
    groups = {g: {"file_count": 0, "record_count": 0, "record_kinds": Counter(), "industry_evidence_counts": Counter()} for g in GROUPS}
    index = CandidateIndex()
    with (output / "phase1_records.jsonl").open("x", encoding="utf-8") as stream:
        for group, path in found:
            relative = path.relative_to(input_root).as_posix()
            source = {"source_id": stable("source", relative, hashes[str(path)]),
                      "company_source_group": group, "filename": path.name,
                      "relative_path": relative, "file_type": path.suffix.lower().lstrip("."),
                      "sha256": hashes[str(path)], "sheet_names": [], "sheets": [],
                      "record_count": 0, "warnings": []}
            inventory["sources"].append(source)
            groups[group]["file_count"] += 1
            try:
                file_type, tables, metadata = parse(path)
                source.update(file_type=file_type, parsing_status="parsed", format_metadata=metadata,
                              sheets=[sheet_inventory(t) for t in tables],
                              sheet_names=[t["name"] for t in tables] if file_type == "xlsx" else [])
                source["warnings"].extend(metadata.get("parse_warnings", []))
            except Exception as exc:
                source.update(parsing_status="unsupported" if isinstance(exc, NotImplementedError) else "failed",
                              error=f"{type(exc).__name__}: {exc}")
                source["warnings"].append(source["error"])
                print(f"{source['parsing_status']}: {relative}", flush=True)
                continue
            kinds = Counter()
            unnamed, formulas = 0, 0
            for record in source_records(source, tables):
                stream.write(packed(record) + "\n")
                index.add(record)
                source["record_count"] += 1
                kinds[record["record_kind"]] += 1
                groups[group]["record_count"] += 1
                groups[group]["record_kinds"][record["record_kind"]] += 1
                groups[group]["industry_evidence_counts"][record["derived"]["industry_evidence"]["status"]] += 1
                unnamed += sum(c["header_raw"] is None and c["value_raw"] not in (None, "") for c in record["raw_cells"])
                formulas += sum(c["value_type"] == "formula" for c in record["raw_cells"])
            source["record_kinds"] = dict(kinds)
            source["populated_unnamed_cells"] = unnamed
            source["formula_cells"] = formulas
            if unnamed:
                source["warnings"].append(f"{unnamed} populated cells have no header; retained positionally without guessed semantics")
            for sheet in source["sheets"]:
                if sheet["duplicate_headers"]:
                    source["warnings"].append(f"{sheet['sheet']}: duplicate headers retained: {sheet['duplicate_headers']}")
                if len(sheet["row_width_counts"]) > 1:
                    source["warnings"].append(f"{sheet['sheet']}: nonuniform row widths {sheet['row_width_counts']}")
                if sheet["blank_record_count"]:
                    source["warnings"].append(f"{sheet['sheet']}: {sheet['blank_record_count']} explicit blank rows retained as unresolved")
                if sheet["merged_ranges"]:
                    source["warnings"].append(f"{sheet['sheet']}: {len(sheet['merged_ranges'])} merged ranges retained without propagating values")
            print(f"parsed: {relative}: {source['record_count']} records", flush=True)
    inventory["source_groups"] = groups
    candidates = index.candidates()
    candidate_payload = {"schema_version": "phase1.1", "candidate_count": len(candidates), "candidates": candidates}
    write_json(output / "phase1_candidates.json", candidate_payload)
    try:
        inventory["validation"] = validate(input_root, inventory, output / "phase1_records.jsonl", candidates, hashes)
        persisted = json.loads((output / "phase1_candidates.json").read_text(encoding="utf-8"))
        if persisted != candidate_payload:
            raise ValueError("Serialized candidate output mismatch")
    except Exception as exc:
        inventory["validation"] = {"passed": False, "checks": {}, "error": f"{type(exc).__name__}: {exc}"}
    inventory["coverage_status"] = "complete" if all(s["parsing_status"] == "parsed" for s in inventory["sources"]) else "partial"
    inventory["candidate_counts"] = dict(Counter(c["candidate_type"] for c in candidates))
    write_json(output / "phase1_inventory.json", inventory)
    if json.loads((output / "phase1_inventory.json").read_text(encoding="utf-8")) != inventory:
        raise ValueError("Serialized inventory output mismatch")
    (output / "phase1_report.md").write_text(report(inventory, candidates), encoding="utf-8")
    print(packed({"validation": inventory["validation"], "coverage": inventory["coverage_status"],
                  "source_groups": groups, "candidate_count": len(candidates), "output_dir": str(output)}))
    return 0 if inventory["validation"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

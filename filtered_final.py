#filtered_final
import json

input_file = "/Users/anushkakatiyar/Desktop/reflexion/programming_runs/final_json.jsonl"
output_file = "final_filtered.jsonl"

records = {}

with open(input_file, "r") as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            name = data.get("name")

            if not name:
                continue

            # If not seen before, add it
            if name not in records:
                records[name] = data
            else:
                # Prefer the one where is_solved is True
                prev = records[name]
                prev_solved = prev.get("is_solved", False)
                curr_solved = data.get("is_solved", False)

                # Case 1: current solved and previous not solved → replace
                if curr_solved and not prev_solved:
                    records[name] = data
                # Case 2: both unsolved but current has more info (non-empty reflections, etc.)
                elif not prev_solved and not curr_solved:
                    if len(data.get("reflections", [])) > len(prev.get("reflections", [])):
                        records[name] = data
                # Case 3: both solved — keep the latest one
                elif curr_solved and prev_solved:
                    records[name] = data

        except json.JSONDecodeError:
            print(f"⚠️ Skipping invalid JSON line: {line[:50]}...")

# Write filtered results
with open(output_file, "w") as out:
    for v in records.values():
        out.write(json.dumps(v) + "\n")

# Compute accuracy
total = len(records)
solved = sum(1 for v in records.values() if v.get("is_solved") is True)
accuracy = solved / total if total > 0 else 0

print(f"✅ Filtered results written to {output_file}")
print(f"📊 Summary: {solved} / {total} solved ({accuracy:.2%} accuracy)")

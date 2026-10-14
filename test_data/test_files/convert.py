import csv

input_file = "test_data1.csv"
output_file = "test_data_dialect_2.csv"

with (
    open(input_file, mode="r", newline="", encoding="utf-8") as infile,
    open(output_file, mode="w", newline="", encoding="utf-8") as outfile,
):
    reader = csv.reader(infile, delimiter=",")
    writer = csv.writer(outfile, delimiter=":")

    for row in reader:
        writer.writerow(row)

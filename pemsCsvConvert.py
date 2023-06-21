folder = "./PEMS"
id_filename = f"{folder}/PEMS03.txt"
input_filename = f"{folder}/distance.csv"
middle_filename = f"{folder}/distance_m.csv"
output_filename = f"{folder}/PEMS.csv"

with open(input_filename, "r") as infile:
    data = infile.readlines()
    infile.close()

with open(middle_filename, "w") as outfile:
    for s in data:
        if s.replace("\n", "").replace(" ", "") == "":
            continue
        outfile.write(s.replace("\n", "") + "\n")
    outfile.close()

with open(id_filename, 'r') as f:
    id_dict = {int(i): idx for idx, i in enumerate(f.read().strip().split('\n'))}

data = []
cnt = 0

with open(output_filename, 'w') as outfile:
    with open(middle_filename, 'r') as infile:
        for line in infile.readlines():
            cnt = cnt + 1
            if cnt != 1:
                line = line.replace("\n", "").split(",")
                line = f"{id_dict[int(line[0])]},{id_dict[int(line[1])]},{float(line[2])}\n"
            outfile.write(line)
        infile.close()
    outfile.close()
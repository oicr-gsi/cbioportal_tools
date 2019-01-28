import os

# Generates fake files to allow testing of a Patient and Sample ID Generator
if not os.stat("fakes/"):
    os.mkdir("fakes/")
os.chdir("fakes/")

for each in range(10):
    f = open("GECCO_" + str(each) + "_L.vcf.gz", "w+")
    file.close(f)


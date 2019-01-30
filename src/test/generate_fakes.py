import os

# Generates fake files to allow testing of a Patient and Sample ID Generator
try:
    os.stat("fakes/")
except OSError:
    os.mkdir("fakes/")
os.chdir("fakes/")

for each in range(10):
    f = open("GECCO_" + str(each).zfill(4) + "_Li_R.vcf.gz", "w+")
    file.close(f)
    f = open("GECCO_" + str(each).zfill(4) + "_Ly_P.vcf.gz", "w+")
    file.close(f)


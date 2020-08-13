#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

library(CNTools)
library(optparse)
library(deconstructSigs)

print("TESTING")
#Load in segmentation data
segData <- read.delim(args[1], header=TRUE)

#Get gene info
geneInfo <- read.delim(args[2], sep="\t", header=TRUE)

# Set thresholds
print("setting thresholds")
gain=as.numeric(args[3])
amp=as.numeric(args[4])
htz=as.numeric(args[5])
hmz=as.numeric(args[6])

#make CN matrix gene level
print("converting seg")
cnseg <- CNSeg(segData)
rdByGene <- getRS(cnseg, by="gene", imput=FALSE, XY=FALSE, geneMap=geneInfo, what="median")
reducedseg <- rs(rdByGene)

#Export data to csv
write.table(data.frame("Hugo_Symbol"=rownames(reducedseg), reducedseg, check.names=FALSE),
            file=paste0(args[7], "/data_reducedseg.txt"), sep="\t", row.names=FALSE, quote=FALSE)

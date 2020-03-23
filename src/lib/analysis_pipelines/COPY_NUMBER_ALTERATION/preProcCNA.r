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
#tempsave = gsub(".txt", "_temp.txt", args[1])
#write.table(tempsave, sep="\t")
#print("TESTING")
write.table(data.frame("Hugo_Symbol"=rownames(reducedseg), reducedseg, check.names=FALSE),
            file=paste0(args[7], "/data_reducedseg.txt"), sep="\t", row.names=FALSE, quote=FALSE)

# some reformatting and return log2cna data
df_cna <- subset(reducedseg[,c(5, 6:ncol(reducedseg))], !duplicated(reducedseg[,c(5, 6:ncol(reducedseg))][,1]))

#TESTING
print('################################33')
print(colnames(df_cna))
print('################################33')
#TESTING

colnames(df_cna) <- c("Hugo_Symbol", colnames(df_cna)[2:ncol(df_cna)])

#TESTING#
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$')
print(colnames(df_cna))
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$')
#TESTING#

# set thresholds and return 5-state matrix
print("thresholding cnas")
df_cna_thresh <- df_cna
df_cna_thresh[,c(2:ncol(df_cna))] <- sapply(df_cna_thresh[,c(2:ncol(df_cna))], as.numeric)

write.table(data.frame("Hugo_Symbol"=rownames(df_cna_thresh), df_cna_thresh, check.names=FALSE),
            file=paste0(args[7], "/cna_threshold_final.txt"), sep="\t", row.names=FALSE, quote=FALSE)

# threshold data
for (i in 2:ncol(df_cna_thresh))
{
	df_cna_thresh[,i] <- ifelse(df_cna_thresh[,i] > amp, 2, 
				    ifelse(df_cna_thresh[,i] < hmz, -2, 
					   ifelse(df_cna_thresh[,i] > gain & df_cna_thresh[,i] <= amp, 1, 
						  ifelse(df_cna_thresh[,i] < htz & df_cna_thresh[,i] >= hmz, -1, 0))))}

# fix rownames of log2cna data
rownames(df_cna) <- df_cna$Hugo_Symbol
df_cna$Hugo_Symbol <- NULL
df_cna <- signif(df_cna, digits=4)

# fix rownames of thresholded data
row.names(df_cna_thresh) <- df_cna_thresh[,1]
df_cna_thresh <- df_cna_thresh[,-1] # matrix where row names are genes, samples are columns

keep_genes <- readLines(args[8])
df_cna <- df_cna[row.names(df_cna) %in% keep_genes,]
df_cna_thresh <- df_cna_thresh[row.names(df_cna_thresh) %in% keep_genes,]

write.table(data.frame("Hugo_Symbol"=rownames(df_cna), df_cna, check.names=FALSE),
	    file=paste0(args[7], "/data_log2CNA.txt"), sep="\t", row.names=FALSE, quote=FALSE)
write.table(data.frame("Hugo_Symbol"=rownames(df_cna_thresh), df_cna_thresh, check.names=FALSE),
	    file=paste0(args[7], "/data_CNA.txt"), sep="\t", row.names=FALSE, quote=FALSE)


#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# Get TCGA comparitor
load(file=args[1])
df_tcga <- get(args[2])
write.table(data.frame("Hugo_Symbol"=rownames(df_tcga), df_tcga, check.names=FALSE),
	    file=paste0(args[3], "/tcga_temp.txt"), sep="\t", row.names=FALSE, quote=FALSE)

library(optparse)
library(CNTools)

option_list = list(
  make_option(c("-s", "--segfile"), type="character", default=NULL, help="concatenated seg file"),
  make_option(c("-g", "--genebed"), type="character", default=NULL, help="gene bed for segmentation"),
  make_option(c("-l", "--genelist"), type="character", default=NULL, help="subset to these genes"),
  make_option(c("-o","--outputfile"), type="character",default=NULL,help="file to output data matrix")
)
opt_parser <- OptionParser(option_list=option_list);
opts <- parse_args(opt_parser);

### check required arguements
required=c("segfile","genebed","outputfile")
for(req in required){
  if(is.null(opts[[req]])){
    print_help(opt_parser)
    msg<-paste("missing ",req)
    stop(msg)
  }
}

segData <- read.delim(opts$segfile, header=TRUE) # segmented data already
segData$chrom <- gsub("chr","",segData$chrom)
geneInfo <- read.delim(opts$genebed, sep="\t", header=TRUE)

#### put seg data into a CNSeq object
cnseg <- CNSeg(segData)
## calculate reduced segments by gene, using median value of segments
rsByGene <- getRS(cnseg, by="gene", imput=FALSE, XY=FALSE, geneMap=geneInfo, what="median")
## extract the matrix
df.rs <- rs(rsByGene)
df.rs<-df.rs[,5:ncol(df.rs)]
df.rs<-df.rs[!duplicated(df.rs),]
colnames(df.rs)[1]<-"Hugo_Symbol"

write.table(df.rs,file=opts$outputfile, sep="\t", row.names=FALSE, quote=FALSE)

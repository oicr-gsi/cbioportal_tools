#! /usr/bin/awk -f


BEGIN {
	{ FS="\t"}
	{ OFS=FS }
}

{
	if(FNR==1)
	{
		print
	}
	else
	{
		{ sum=0 }
		for(i = 2; i <= NF; i++)
		{
			sum+=int($i)
		}

		{ mu= (sum/(NF-1)) }

		{ sigma=0 }
		for(i = 2; i <= NF; i++)
		{
			sigma += ((($i-mu)^2)/(NF-1))
		}
		{ sigma = (sigma ^ (1/2)) }

		{ zscore[1] = $1 }
		for(i = 2; i <= NF; i++)
		{
			zscore[i] = (sigma==0) ? 0 : ($i-mu)/sigma
		}

		for( i in zscore)
		{
			printf "%s\t",zscore[i];
		}
		print ""
	}
}

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
		for(i = 2; i <= NF; i++)
		{
			if($i > ampl)
			{
				$i = 2
			}
			else if($i < hmzd)
			{
				$i = -2
			}
			else if(($i > gain) && (i <= ampl))
			{
				$i = 1
			}
			else if(($i < htzd) && (i >= hmzd))
			{
				$i = -1
			}
			else
			{
				$i = 0
			}
		}

		for(i = 1; i <= NF; i++)
		{
			printf "%s\t",$i;
		}
		print ""
	}
}

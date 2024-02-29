## ----setup, include=FALSE-----------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)


## -----------------------------------------------------------------------------
library(jsonlite)
library(dplyr)


## -----------------------------------------------------------------------------
winter_data<-read.csv('concept-lists/Winter-2022-98.tsv',sep='\t') ##Winter-Overt-Marking
affix_colex<-read.csv('concept-lists/List-2023-1308.tsv',sep='\t') ##List-Partial-Colexifications
urban_data<-read.csv('concept-lists/Urban-2011-160.tsv',sep='\t')  ##Urban-Indo-Aryan
dss<-read.csv('concept-lists/Zalizniak-2024-4583.tsv',sep='\t')  ##Zalizniak-DatSemShift


## -----------------------------------------------------------------------------
winter_df<-data.frame(stringsAsFactors = F) ##initialising dataframe

for (i in seq (1,nrow(winter_data))) ##loop on imported data
{
  concept<-winter_data$ENGLISH[i]
  ##ordering sources
  sources<-fromJSON(winter_data$SOURCE_CONCEPTS[i])
  for(j in seq(1,nrow(sources)))
  {
    source<-sources$NAME[j]
    df<-data.frame(source=source,target=concept,
               overt_marking=sources$OvertMarking[j],stringsAsFactors = F)
    winter_df<-rbind(winter_df,df)
  }
  ##ordering targets
  targets<-fromJSON(winter_data$TARGET_CONCEPTS[i])
    for(j in seq(1,nrow(targets)))
  {
    target<-targets$NAME[j]
    df<-data.frame(source=concept,target=target,
               overt_marking=targets$OvertMarking[j],stringsAsFactors = F)
    winter_df<-rbind(winter_df,df)
  }
}
winter_df<-winter_df[-which(duplicated(winter_df)),] ##removing duplicates
rownames(winter_df)<-seq(1,nrow(winter_df)) ##renaming rows



## -----------------------------------------------------------------------------
urban_df<-data.frame(stringsAsFactors = F) ##initialising dataframe

for (i in seq (1,nrow(urban_data))) ##loop on imported data
{
  concept<-urban_data$ENGLISH[i]
  ##ordering targets
  targets<-fromJSON(urban_data$TARGET_CONCEPTS[i])
  if(length(targets)>0)
  {
    for(j in seq(1,nrow(targets)))
    {
      target<-targets$NAME[j]
      df<-data.frame(source=concept,target=target,
                 direction=targets$IndoAryanShift[j],stringsAsFactors = F)
      urban_df<-rbind(urban_df,df)
    }
  }
}
urban_df<-urban_df[urban_df$direction==1,] ##removing data for which we do not have direction
urban_df$direction<-NULL ##removing useless column
###removing duplicates, aka pairs of concepts for which we have evidence of shift in both directions
dupl<-which(duplicated(data.frame(t(apply(urban_df[1:2], 1, sort)))))
to_remove<-dupl
for(i in dupl)
{
  s<-urban_df$source[i]
  t<-urban_df$target[i]
  to_remove<-c(to_remove,which(urban_df$target==s & urban_df$source==t))
}
urban_df<-urban_df[-to_remove,]
rownames(urban_df)<-seq(1,nrow(urban_df))


## -----------------------------------------------------------------------------
affix_colex_df<-data.frame(stringsAsFactors = F) ##initialising dataframe

for (i in seq (1,nrow(affix_colex))) ##loop on imported data
{
  concept<-tolower(affix_colex$ENGLISH[i])
  ##ordering targets
  targets<-fromJSON(affix_colex$TARGET_CONCEPTS[i])
  if(length(targets)>0)
  {
    for(j in seq(1,nrow(targets)))
    {
      target<-tolower(targets$NAME[j])
      df<-data.frame(source=concept,target=target,
                 overt_marking_lang=targets$AffixLngs[j],overt_marking_fam=targets$AffixFams[j],stringsAsFactors = F)
      affix_colex_df<-rbind(affix_colex_df,df)
    }
  }
}


## -----------------------------------------------------------------------------
dss_df<-data.frame(stringsAsFactors = F) ##initialising dataframe

for (i in seq (1,nrow(dss))) ##loop on imported data
{
  concept<-dss$ENGLISH[i]
  ##ordering targets
  targets<-fromJSON(dss$TARGET_CONCEPTS[i])
  if(length(targets)>0)
  {
    for(j in seq(1,nrow(targets)))
    {
      target<-targets$NAME[j]
      df<-data.frame(source=concept,target=target,polysemy=targets$Polysemy[j], derivation=targets$Derivation[j],polysemy_fam=targets$PolysemyByFamily[j], derivation_fam=targets$DerivationByFamily[j],stringsAsFactors = F)
      dss_df<-rbind(dss_df,df)
    }
  }
}


## -----------------------------------------------------------------------------
winter_df<-left_join(winter_df,winter_df,by=c("source"="target","target"="source")) ##adding opposite overt marking
##renaming column
winter_df<-winter_df%>%rename("opposite_overt_marking"="overt_marking.y")
winter_df<-winter_df%>%rename("overt_marking"="overt_marking.x")

###removing duplicates
dupl<-which(duplicated(data.frame(t(apply(winter_df[1:2], 1, sort)))))
to_remove<-c()
for(i in dupl)
{
  s<-winter_df$source[i]
  t<-winter_df$target[i]
  annotations<-winter_df[winter_df$source==s&winter_df$target==t,3:4]
  annotations_opposite<-winter_df[winter_df$source==t&winter_df$target==s,3:4]
  if(all(annotations==annotations_opposite[2:1]))
  {
    to_remove<-c(to_remove,i)
  }
  else
  {print(i)}
}
winter_df<-winter_df[-to_remove,]
rownames(winter_df)<-seq(1,nrow(winter_df))

source("check_prediction.R")
output<-check_prediction(winter_df,urban_df)
paste("Number instances accepted:", output$confirmed )
paste("Number instances rejected:", output$not_confirmed)
paste("N:", output$N)
paste("Precision:",round(output$prec,digits=2))



## -----------------------------------------------------------------------------
affix_colex_df$overt_marking_fam<-NULL ##working only with languages
merged_df<-left_join(affix_colex_df,affix_colex_df,by=c("source"="target","target"="source"))
##renaming columns (languages)
merged_df<-merged_df%>%rename("overt_marking"="overt_marking_lang.x")
merged_df<-merged_df%>%rename("opposite_overt_marking"="overt_marking_lang.y")

# ##renaming columns (families)
# merged_df<-merged_df%>%rename("overt_marking"="overt_marking_fam.x")
# merged_df<-merged_df%>%rename("opposite_overt_marking"="overt_marking_fam.y")

##adding 0s where we have NAs
merged_df$opposite_overt_marking[is.na(merged_df$opposite_overt_marking)]<-0
merged_df$overt_marking[is.na(merged_df$overt_marking)]<-0

source("check_prediction.R")
output<-check_prediction(merged_df,urban_df)

paste("Number instances accepted:", output$confirmed )
paste("Number instances rejected:", output$not_confirmed)
paste("N:", output$N)
paste("Precision:",round(output$prec,digits=2))




## -----------------------------------------------------------------------------
sel<-dss_df[which(dss_df$polysemy>0),] ###selecting only the ones that have polysemy evidence

sel$polysemy_fam<-NULL
sel$derivation_fam<-NULL

##removing duplicates (rows for which we have evidence in both directions)
rownames(sel)<-seq(1,nrow(sel))
dupl<-which(duplicated(data.frame(t(apply(sel[1:2], 1, sort)))))
to_remove<-dupl
for(i in dupl)
{
  s<-sel$Source[i]
  t<-sel$Target[i]
  to_remove<-c(to_remove,which(sel$Target==s & sel$Source==t))
}
sel<-sel[-to_remove,]
rownames(sel)<-seq(1,nrow(sel))

##removing useless columns
sel$polysemy<-NULL
sel$derivation<-NULL
sel$polysemy_fam<-NULL
sel$derivation_fam<-NULL

affix_colex_df$overt_marking_fam<-NULL ##working only with languages
merged_df<-left_join(affix_colex_df,affix_colex_df,by=c("source"="target","target"="source"))
##renaming columns (languages)
merged_df<-merged_df%>%rename("overt_marking"="overt_marking_lang.x")
merged_df<-merged_df%>%rename("opposite_overt_marking"="overt_marking_lang.y")

# ##renaming columns (families)
# merged_df<-merged_df%>%rename("overt_marking"="overt_marking_fam.x")
# merged_df<-merged_df%>%rename("opposite_overt_marking"="overt_marking_fam.y")

##adding 0s where we have NAs
merged_df$opposite_overt_marking[is.na(merged_df$opposite_overt_marking)]<-0
merged_df$overt_marking[is.na(merged_df$overt_marking)]<-0


source("check_prediction.R")
output<-check_prediction(merged_df,sel)
paste("Number instances accepted:", output$confirmed )
paste("Number instances rejected:", output$not_confirmed)
paste("N:", output$N)
paste("Precision:",round(output$prec,digits=2))




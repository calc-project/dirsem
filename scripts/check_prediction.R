check_prediction<-function(overt_marking_data,gold_standard,hp_type)
  ######function that checks the prediction of directionality of semantic change
  ####from overt marking data (given in input) against a gold standard (given in input)
  ###hp_type is the type of hypothesis. It can be either "strict" (Urban, 2011) 
  ###or "relaxed" (Bocklage et al, 2024)
{
  if(hp_type=="strict") ########strict hypothesis (Urban, 2011)
  {
    prediction_df<-overt_marking_data[overt_marking_data$overt_marking>0 
                                      & overt_marking_data$opposite_overt_marking==0,1:2]
    ###strict hypothesis
    t<-overt_marking_data[overt_marking_data$overt_marking==0 
                          & overt_marking_data$opposite_overt_marking>0,c(2,1)]
  }
  
  if(hp_type=="relaxed") ########relaxed hypothesis (Bocklage et al, 2024)
  {
    prediction_df<-overt_marking_data[overt_marking_data$overt_marking > 
                                        overt_marking_data$opposite_overt_marking,1:2]
    ######relaxed hypothesis
    t<-overt_marking_data[overt_marking_data$overt_marking< 
                          overt_marking_data$opposite_overt_marking,c(2,1)]
  }
  
    t<-t%>%rename(source=target,target=source)
    prediction_df<-rbind(prediction_df,t)  ##attacching the reverse pairs
    prediction_df<-prediction_df[!duplicated(prediction_df),] ##removing duplicates
    # any(duplicated(data.frame(t(apply(prediction_df[1:2], 1, sort)))))##sanity check
    ##merging gold standard and predictions
    gold_standard$direction<-1
    final_df<-left_join(prediction_df,gold_standard)
    gold_standard$direction<-0 ##checking for wrong predictions
    final_df<-left_join(final_df,gold_standard,by=c('source'='target','target'='source'))
    final_df<-final_df[!(is.na(final_df$direction.x)&is.na(final_df$direction.y)),]

  
  ##N: number of pairs for which we could have predicted a direction and checked
  ##against the gold standard
  gold_standard$direction<-NULL
  gold_standard$gold_standard<-1
  t<-left_join(overt_marking_data,gold_standard) 
  t<-left_join(t,gold_standard,by=c('source'='target','target'='source'))
  t<-t[!duplicated(data.frame(t(apply(t[1:2], 1, sort)))),] ##removing duplicates
  N<-length(which(!(is.na(t$gold_standard.x)&is.na(t$gold_standard.y))))
  ##number of instances for which we can check the prediction
  confirmed<-length(which(final_df$direction.x==1)) ###true positive

  not_confirmed<-length(which(final_df$direction.y==0))  ###false positive
 
  ###computing precision, recall and F1
  prec<-confirmed/(confirmed+not_confirmed)
  rec<-confirmed/N
  F1<-2*(prec*rec)/(prec+rec)

  return(data.frame(N=N,confirmed=confirmed,not_confirmed=not_confirmed,prec=prec,
                    rec=rec,F1=F1,stringsAsFactors = F))  ##returning dataframe with results
  
  
}
# NYCU-Intro-AI-Final-Project
111 第2學期 陳奕廷教授  
Final Project of Introduction to Artificial Intelligence
## Group Member
110550014 吳權祐  
110550060 關立  
110550082 王邦碩  
110550130 劉秉驊  
## Topic
Popularity Prediction of Article Online

## Description
Target :<br/> 
An article from the Internet is going to be given, and we look forward to the prediction of its popularity online *(including hits, likes, and shares)*.<br/>
<br/>
Implementation Summary : 
1. Find some useful dataset
2. Choose the suitable attributes
3. Build the Random Decision Forests to achieve our goal
   - Use the chosen attributes as the decision nodes
   - We will try other algorithms or models to obtain better performance<br/>
4. We need to find the useful NLP model to process the articles to abstract the attributes we want
   
Questions We Think We May Face : 
- We have difficulty in fetching the capable dataset.
- There may be some ambiguous attributes we are not able to determine.
- The accuracy may not reach our expectation.


## Implementation

### Data Collection
- Use NYTimes API to scrap the article information and NYTimes Community to scrap the comment information, mainly n_comment
- Period :<br/>Data from 2021 - 2022
- Train Test Split :<br/>
  Split data into train and test by the ratio 2/3
- Modified : <br/>
  We find out that there are a lot 0 comment article in the dataset, so we are interest with that would they effect the model a lot. Then we make two version of dataset with the difference in deleting the 0 comment datas

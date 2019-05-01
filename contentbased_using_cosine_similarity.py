#!/usr/bin/env python


# Content Based recommendation system with the engineered features 
# subway access, crime score etc, along with other features

import pandas as pd
import numpy as np
df = pd.read_csv('data/listings_with_transitscore_and_crimescore_normalized.csv')
df = df.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], axis=1)

df1 = pd.read_csv('data/shared_final_prediction_file.csv')
df1 = df1.drop(columns=['Unnamed: 0'], axis=1)


print("read csv's")
df2 = df1.groupby('listing_id', as_index=False).aggregate({'polarity': 'mean'})


print("Creating Item profile")
# Create Item Profile
df_item_profile = df[['id','host_id', 'neighbourhood_group',
                      'room_type','price', 'minimum_nights', 'availability_365','transitscore','crime_score' ]]

df_item_profile = df_item_profile.rename(columns={'id':'listing_id'})

df_item_profile = pd.get_dummies(df_item_profile, columns=["neighbourhood_group"])
df_item_profile = pd.get_dummies(df_item_profile, columns=["room_type"]) 
df_item_profile = df_item_profile.merge(df2, how='left') # append  polarity, aggregated by listing_id
df_item_profile = df_item_profile.drop(columns=["host_id"])
df_item_profile = df_item_profile.fillna(0)

print("Item profile created, creating user profile next")

#Create User Profile
df_user_profile =  df1
df_relation = df1 # Save for later

#keep building user profile

df_temp_item_profile = df_item_profile.drop(columns=["polarity"])
df_user_profile = df_user_profile.merge(df_temp_item_profile, how='left')

df_user_profile = df_user_profile.fillna(0)

print("user profile created")
from functools import reduce 
def or_agg(series):
       return reduce(lambda x, y: x or y, series)

aggregations = {'polarity':'mean', 
                'price': 'mean',
                'availability_365': 'mean',
                'minimum_nights': 'mean',
                'neighbourhood_group_Bronx':or_agg, 
                'neighbourhood_group_Brooklyn': or_agg, 
                'neighbourhood_group_Manhattan':or_agg,
                'neighbourhood_group_Queens': or_agg,
                 'neighbourhood_group_Staten Island': or_agg,
                 'room_type_Entire home/apt': or_agg,
                'room_type_Private room': or_agg,
                'room_type_Shared room': or_agg,
                 'transitscore': 'mean',
                 'crime_score': 'mean' }
df_user_profile = df_user_profile.groupby('reviewer_id', as_index=False).aggregate(aggregations)


print("aggregate generated")


df_user_profile.to_csv('data/user_profile_withscores.csv')




#min-max normalization for user profile
ss,s0 = np.split(df_user_profile,[1],axis=1)
df_user_profile = pd.concat([ss,(s0 - s0.mean()) / (s0.max() - s0.min())], axis=1)




#min-max normalization for item profile
ss,s0 = np.split(df_item_profile,[1],axis=1)
df_item_profile = pd.concat([ss,(s0 - s0.mean()) / (s0.max() - s0.min())],axis=1)




from sklearn.metrics.pairwise import cosine_similarity
def cosine_sim(a,b):
    return  cosine_similarity(a,b)




df_similarity = pd.DataFrame(columns=["reviewer_id", 'listing_id', 'similarity'])

i=1  
for relation in df_relation.iterrows():
    
    reviewer_id = relation[1]["reviewer_id"]
    j=0
    for item in df_item_profile.iterrows():
        listing_id = item[1]["listing_id"]
    
        df_v1 = df_user_profile.loc[df_user_profile.reviewer_id == reviewer_id]
    
        v1 = df_v1.drop(columns=["reviewer_id"])
  
        df_v2 = df_item_profile.loc[df_item_profile.listing_id == listing_id]
        v2 = df_v2.drop(columns=["listing_id"])
        sim = cosine_sim(v1, v2)
        df_similarity = df_similarity.append({"reviewer_id":reviewer_id, "listing_id":listing_id,"similarity":sim[0][0]}, ignore_index=True)
        j+=1
        if i%5000 == 0:
            print("%d:%d user:%f, listing:%f" % (i,j, reviewer_id, listing_id))
            print(sim)
            df_similarity.to_csv('data/temp_sim_withscores.csv', header=True, index = False)
    i +=1
df_similarity.to_csv('data/cosine_sim_withscores.csv', header=True, index = False)
sprint ("done")






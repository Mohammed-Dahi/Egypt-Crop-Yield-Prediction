import json, numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

T="Yield"
NUM=["Yield_Lag1","Yield_Lag2","Production_Lag1","Area_Lag1","Yield_RollingMean_3Y","Area_Growth_Lag1","Production_Growth_Lag1"]
train=pd.read_csv("train_data.csv").sort_values("Year").reset_index(drop=True)
test=pd.read_csv("test_data.csv")

def ev(y,p): return dict(MAE=mean_absolute_error(y,p),RMSE=float(np.sqrt(mean_squared_error(y,p))),R2=r2_score(y,p))
def prep(df,cols,sc=None):
    X=pd.get_dummies(df[["Item"]+NUM],columns=["Item"],prefix="Item").reindex(columns=cols,fill_value=0).astype(float)
    return X
yrs=sorted(train.Year.unique()); k=int(len(yrs)*.8)
tm=train[train.Year.isin(yrs[:k])]; va=train[train.Year.isin(yrs[k:])]
cols=pd.get_dummies(tm[["Item"]+NUM],columns=["Item"],prefix="Item").columns
Xtr,Xva,Xte=[prep(d,cols) for d in (tm,va,test)]
sc=StandardScaler().fit(Xtr[NUM])
for X in (Xtr,Xva,Xte): X[NUM]=sc.transform(X[NUM])
lin=LinearRegression().fit(Xtr,tm[T])
res={}
res["Baseline"]=ev(test[T],test.Yield_Lag1)
res["Linear Regression"]=ev(test[T],lin.predict(Xte))
tun=[]
for d in [3,4,5,6,7,8,10,12,15]:
    m=DecisionTreeRegressor(max_depth=d,random_state=42).fit(Xtr,tm[T]); tun.append((d,np.sqrt(mean_squared_error(va[T],m.predict(Xva)))))
bd=min(tun,key=lambda x:x[1])[0]
tree=DecisionTreeRegressor(max_depth=bd,random_state=42).fit(Xtr,tm[T])
res["Decision Tree"]=ev(test[T],tree.predict(Xte))
print("best depth",bd)
for k_,v in res.items(): print(k_,{a:round(b,3) for a,b in v.items()})
json.dump(dict(res=res,best_depth=int(bd)),open("metrics_tmp.json","w"))

# ---- refit deployed models on ALL data (train+test)
full=pd.concat([train,test]).reset_index(drop=True)
cols=list(pd.get_dummies(full[["Item"]+NUM],columns=["Item"],prefix="Item").columns)
Xf=prep(full,cols); sc=StandardScaler().fit(Xf[NUM]); Xf[NUM]=sc.transform(Xf[NUM])
lin=LinearRegression().fit(Xf,full[T]); tree=DecisionTreeRegressor(max_depth=int(bd),random_state=42).fit(Xf,full[T])
items=sorted(full.Item.unique())
def tj(t,names):
    s=t.tree_
    def rec(i):
        if s.children_left[i]==-1: return round(float(s.value[i][0][0]),1)
        return [names[s.feature[i]],round(float(s.threshold[i]),4),rec(s.children_left[i]),rec(s.children_right[i])]
    return rec(0)
last={}
for it,g in full.sort_values("Year").groupby("Item"):
    r=g.iloc[-1]; last[it]=dict(y=int(r.Year),Y=float(r[T]),Y1=float(r.Yield_Lag1),A=float(r.Area_Lag1),P=float(r.Production_Lag1))
mdl=dict(items=items,num=NUM,mean=[round(float(x),6) for x in sc.mean_],scale=[round(float(x),6) for x in sc.scale_],
 lin=dict(b=float(lin.intercept_),w=dict(zip(cols,[round(float(c),4) for c in lin.coef_]))),
 tree=tj(tree,cols),metrics=res,depth=int(bd),last=last,
 nrows=len(full),years=[int(full.Year.min()),int(full.Year.max())])
json.dump(mdl,open("model.json","w"),separators=(",",":"))
import os;print("model.json KB",os.path.getsize("model.json")/1024)
# sanity: python vs manual
x=Xf.iloc[[5]]; print(lin.predict(x),tree.predict(x))
print(full[[ "Item"]].iloc[5].values, last[items[0]])

import streamlit as st
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Brownie Book",page_icon="🍫",layout="wide")
sb=create_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])

PRODUCTS={
"250g Classic":(170,91),"250g Milk Chocolate":(185,106),"250g White Chocolate":(180,100),
"250g Triple Chocolate":(200,120),"250g Double Chocolate":(190,110),"250g Oreo":(175,90),
"500g Classic":(270,126),"500g Milk Chocolate":(290,146),"500g White Chocolate":(285,140),
"500g Triple Chocolate":(310,164),"500g Double Chocolate":(300,154),"500g Oreo":(280,160),
"Cookie Pie Dark":(175,85),"Cookie Pie White":(180,88),"Cookie Pie Milk":(185,94),
"Brownie Bites":(169,86)}

st.markdown("""<style>
#MainMenu,footer,header{visibility:hidden}.block-container{padding:1rem 1rem 4rem;max-width:1100px}
.hero{padding:1.4rem 1.5rem;border-radius:24px;background:linear-gradient(135deg,#24130d,#5a2c1c);color:white;margin-bottom:1rem}
.hero h1{margin:0}.hero p{margin:.2rem 0 0;opacity:.8}.card{padding:1rem;border:1px solid #eadfd9;border-radius:18px;background:white;min-height:100px}
.label{font-size:.82rem;color:#766b65}.value{font-size:1.5rem;font-weight:700;margin-top:.3rem}.section{font-size:1.2rem;font-weight:700;margin:1.1rem 0 .6rem}
div.stButton>button{border-radius:14px;min-height:44px;font-weight:600}
</style>""",unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page="Dashboard"
def go(p): st.session_state.page=p; st.experimental_rerun()

nav=st.columns(4)
for c,label,p in zip(nav,["🏠 Dashboard","➕ Add Sale","🛒 Purchase","📊 Reports"],["Dashboard","Add Sale","Purchase","Reports"]):
    with c:
        if st.button(label,use_container_width=True): go(p)

st.markdown('<div class="hero"><h1>🍫 Brownie Book</h1><p>Your brownie-business money tracker — synced online</p></div>',unsafe_allow_html=True)

today=date.today().isoformat(); month=date.today().replace(day=1).isoformat()
sales=sb.table("sales").select("*").order("id",desc=True).execute().data
purchases=sb.table("purchases").select("*").order("id",desc=True).execute().data

def filt(rows,start=None,end=None):
    return [r for r in rows if (not start or str(r["date"])[:10]>=start) and (not end or str(r["date"])[:10]<=end)]

page=st.session_state.page
if page=="Dashboard":
    s=filt(sales,month,today); p=filt(purchases,month,today)
    vals=[sum(float(x["sales"]) for x in s),sum(float(x["profit"]) for x in s),sum(float(x["amount"]) for x in p),sum(int(x["quantity"]) for x in s)]
    st.markdown('<div class="section">This month</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for c,l,v in zip(cols,["💰 Sales","📈 Profit","🛒 Ingredients","📦 Items sold"],vals):
        with c: st.markdown(f'<div class="card"><div class="label">{l}</div><div class="value">{"₹" if l!="📦 Items sold" else ""}{v:,.0f}</div></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        if st.button("➕ Record a sale",use_container_width=True): go("Add Sale")
    with b:
        if st.button("🛒 Record ingredient purchase",use_container_width=True): go("Purchase")
    st.markdown('<div class="section">Recent sales</div>',unsafe_allow_html=True)
    for r in sales[:8]: st.write(f"**{r['product']}** × {r['quantity']} • ₹{float(r['sales']):,.0f} • ₹{float(r['profit']):,.0f} profit • `{str(r['date'])[:10]}`")

elif page=="Add Sale":
    st.markdown('<div class="section">Add a sale</div>',unsafe_allow_html=True)
    with st.form("sale"):
        product=st.selectbox("Product",list(PRODUCTS)); qty=st.number_input("Quantity",1,100,1)
        price,profit=PRODUCTS[product]; st.info(f"₹{price} each • ₹{profit} profit each • Order ₹{price*qty}")
        if st.form_submit_button("Save sale",use_container_width=True):
            sb.table("sales").insert({"date":today,"product":product,"quantity":qty,"sales":price*qty,"profit":profit*qty}).execute()
            st.success("Sale saved to cloud."); st.experimental_rerun()

elif page=="Purchase":
    st.markdown('<div class="section">Add ingredient purchase</div>',unsafe_allow_html=True)
    st.caption("Enter only what you actually spent buying ingredients.")
    with st.form("purchase"):
        item=st.text_input("What did you buy?",placeholder="Chocolate, butter, cocoa powder...")
        amount=st.number_input("Amount spent (₹)",min_value=0.0,step=10.0)
        if st.form_submit_button("Save purchase",use_container_width=True):
            if not item.strip() or amount<=0: st.error("Enter the item and amount.")
            else:
                sb.table("purchases").insert({"date":today,"item":item.strip(),"amount":amount}).execute()
                st.success("Purchase saved to cloud."); st.experimental_rerun()

else:
    st.markdown('<div class="section">Reports</div>',unsafe_allow_html=True)
    mode=st.radio("Period",["This month","All time","Custom"],horizontal=True); start=end=None
    if mode=="This month": start,end=month,today
    elif mode=="Custom":
        a,b=st.columns(2)
        with a: start=st.date_input("From",date.today().replace(day=1)).isoformat()
        with b: end=st.date_input("To",date.today()).isoformat()
    sr=filt(sales,start,end); pr=filt(purchases,start,end)
    cols=st.columns(4)
    for c,l,v in zip(cols,["Sales","Profit","Ingredients","Items sold"],[sum(float(x["sales"]) for x in sr),sum(float(x["profit"]) for x in sr),sum(float(x["amount"]) for x in pr),sum(int(x["quantity"]) for x in sr)]):
        with c: st.metric(l,f"₹{v:,.0f}" if l!="Items sold" else f"{v:,.0f}")
    st.markdown('<div class="section">Sales</div>',unsafe_allow_html=True)
    for r in sr:
        c1,c2,c3,c4,c5,c6=st.columns([1.2,2.5,.6,1,1,.8])
        c1.write(str(r["date"])[:10]);c2.write(r["product"]);c3.write(r["quantity"]);c4.write(f"₹{float(r['sales']):,.0f}");c5.write(f"₹{float(r['profit']):,.0f}")
        if c6.button("🗑️",key=f"d{r['id']}"):
            sb.table("sales").delete().eq("id",r["id"]).execute();st.experimental_rerun()
    st.markdown('<div class="section">Ingredient purchases</div>',unsafe_allow_html=True)
    st.dataframe([{"Date":str(r["date"])[:10],"Item":r["item"],"Amount (₹)":r["amount"]} for r in pr],use_container_width=True)
    st.markdown('<div class="section">Products</div>',unsafe_allow_html=True)
    st.dataframe([{"Product":p,"Selling Price (₹)":v[0],"Profit (₹)":v[1]} for p,v in PRODUCTS.items()],use_container_width=True)

import streamlit as st
from datetime import date
from supabase import create_client

st.set_page_config(
    page_title="Brownie Book",
    page_icon="🍫",
    layout="wide"
)

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# --------------------------------------------------
# PRODUCTS
# price = normal selling price
# profit = profit at normal selling price
# --------------------------------------------------

PRODUCTS = {
    "250g Classic": (170, 91),
    "250g Milk Chocolate": (185, 106),
    "250g White Chocolate": (180, 100),
    "250g Triple Chocolate": (200, 120),
    "250g Double Chocolate": (190, 110),
    "250g Oreo": (175, 90),

    "500g Classic": (270, 126),
    "500g Milk Chocolate": (290, 146),
    "500g White Chocolate": (285, 140),
    "500g Triple Chocolate": (310, 164),
    "500g Double Chocolate": (300, 154),
    "500g Oreo": (280, 160),

    "Cookie Pie Dark": (175, 85),
    "Cookie Pie White": (180, 88),
    "Cookie Pie Milk": (185, 94),

    "Brownie Bites": (169, 86),
}

# --------------------------------------------------
# SPECIAL / TEMPORARY COMBOS
# price = actual customer price
# cost = making cost
# --------------------------------------------------

COMBOS = {
    "299 Combo": (259, 100)
}

# --------------------------------------------------
# UI
# --------------------------------------------------

st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}

.block-container{
    padding:1rem 1rem 4rem;
    max-width:1100px
}

.hero{
    padding:1.4rem 1.5rem;
    border-radius:24px;
    background:linear-gradient(135deg,#24130d,#5a2c1c);
    color:white;
    margin-bottom:1rem
}

.hero h1{
    margin:0
}

.hero p{
    margin:.2rem 0 0;
    opacity:.8
}

.card{
    padding:1rem;
    border:1px solid #eadfd9;
    border-radius:18px;
    background:white;
    min-height:100px
}

.label{
    font-size:.82rem;
    color:#766b65
}

.value{
    font-size:1.5rem;
    font-weight:700;
    margin-top:.3rem
}

.section{
    font-size:1.2rem;
    font-weight:700;
    margin:1.1rem 0 .6rem
}

div.stButton>button{
    border-radius:14px;
    min-height:44px;
    font-weight:600
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "order_items" not in st.session_state:
    st.session_state.order_items = []

if "order_customer" not in st.session_state:
    st.session_state.order_customer = ""


def go(p):
    st.session_state.page = p
    st.rerun()


nav = st.columns(4)

for c, label, p in zip(
    nav,
    ["🏠 Dashboard", "➕ Add Sale", "🛒 Purchase", "📊 Reports"],
    ["Dashboard", "Add Sale", "Purchase", "Reports"]
):
    with c:
        if st.button(label, use_container_width=True):
            go(p)


st.markdown(
    '<div class="hero"><h1>🍫 Brownie Book</h1>'
    '<p>Your brownie-business money tracker — synced online</p></div>',
    unsafe_allow_html=True
)

today = date.today().isoformat()
month = date.today().replace(day=1).isoformat()

sales = (
    sb.table("sales")
    .select("*")
    .order("id", desc=True)
    .execute()
    .data
)

purchases = (
    sb.table("purchases")
    .select("*")
    .order("id", desc=True)
    .execute()
    .data
)


def filt(rows, start=None, end=None):
    return [
        r for r in rows
        if (not start or str(r["date"])[:10] >= start)
        and (not end or str(r["date"])[:10] <= end)
    ]


page = st.session_state.page

# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    s = filt(sales, month, today)
    p = filt(purchases, month, today)

    vals = [
        sum(float(x["sales"]) for x in s),
        sum(float(x["profit"]) for x in s),
        sum(float(x["amount"]) for x in p),
        sum(int(x["quantity"]) for x in s)
    ]

    st.markdown(
        '<div class="section">This month</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    for c, l, v in zip(
        cols,
        ["💰 Sales", "📈 Profit", "🛒 Ingredients", "📦 Items sold"],
        vals
    ):
        with c:
            st.markdown(
                f'<div class="card">'
                f'<div class="label">{l}</div>'
                f'<div class="value">'
                f'{"₹" if l != "📦 Items sold" else ""}'
                f'{v:,.0f}'
                f'</div></div>',
                unsafe_allow_html=True
            )

    a, b = st.columns(2)

    with a:
        if st.button("➕ Record a sale", use_container_width=True):
            go("Add Sale")

    with b:
        if st.button(
            "🛒 Record ingredient purchase",
            use_container_width=True
        ):
            go("Purchase")

    st.markdown(
        '<div class="section">Recent sales</div>',
        unsafe_allow_html=True
    )

    for r in sales[:8]:

        customer = r.get("customer_name", "").strip()

        if customer:
            customer_text = f" • 👤 {customer}"
        else:
            customer_text = ""

        st.write(
            f"**{r['product']}** × {r['quantity']}"
            f"{customer_text}"
            f" • ₹{float(r['sales']):,.0f}"
            f" • ₹{float(r['profit']):,.0f} profit"
            f" • `{str(r['date'])[:10]}`"
        )

# ==================================================
# ADD SALE
# ==================================================

elif page == "Add Sale":

    st.markdown(
        '<div class="section">Add a sale</div>',
        unsafe_allow_html=True
    )

    # ----------------------------------------------
    # CUSTOMER NAME
    # ----------------------------------------------

    customer_name = st.text_input(
        "Customer name (optional)",
        value=st.session_state.order_customer,
        placeholder="For your reference"
    )

    st.session_state.order_customer = customer_name

    st.markdown(
        '<div class="section">Add items to this order</div>',
        unsafe_allow_html=True
    )

    # ----------------------------------------------
    # ADD ITEM
    # ----------------------------------------------

    item_type = st.radio(
        "Type",
        ["Product", "Combo"],
        horizontal=True
    )

    if item_type == "Product":

        selected_item = st.selectbox(
            "Product",
            list(PRODUCTS.keys())
        )

        item_price, item_profit = PRODUCTS[selected_item]

        # Cost = selling price - normal profit
        item_cost = item_price - item_profit

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.caption(
            f"₹{item_price} each • "
            f"₹{item_profit} profit each at normal price"
        )

    else:

        selected_item = st.selectbox(
            "Combo",
            list(COMBOS.keys())
        )

        item_price, item_cost = COMBOS[selected_item]

        item_profit = item_price - item_cost

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.caption(
            f"Customer price ₹{item_price} each • "
            f"Cost ₹{item_cost} each • "
            f"Profit ₹{item_profit} each"
        )

    if st.button(
        "➕ Add to order",
        use_container_width=True
    ):

        st.session_state.order_items.append({
            "product": selected_item,
            "quantity": int(qty),
            "price": float(item_price),
            "cost": float(item_cost),
            "normal_profit": float(item_profit)
        })

        st.success(f"{selected_item} added to order.")

    # ----------------------------------------------
    # CURRENT ORDER
    # ----------------------------------------------

    if st.session_state.order_items:

        st.markdown(
            '<div class="section">Current order</div>',
            unsafe_allow_html=True
        )

        normal_total = 0
        total_cost = 0
        total_quantity = 0

        for i, item in enumerate(
            st.session_state.order_items
        ):

            item_total = (
                item["price"] * item["quantity"]
            )

            item_total_cost = (
                item["cost"] * item["quantity"]
            )

            normal_total += item_total
            total_cost += item_total_cost
            total_quantity += item["quantity"]

            c1, c2, c3, c4 = st.columns(
                [3, 1, 1.5, 0.8]
            )

            c1.write(
                f"**{item['product']}**"
            )

            c2.write(
                f"× {item['quantity']}"
            )

            c3.write(
                f"₹{item_total:,.0f}"
            )

            if c4.button(
                "🗑️",
                key=f"remove_item_{i}"
            ):
                st.session_state.order_items.pop(i)
                st.rerun()

        st.divider()

        st.write(
            f"**Normal order total: ₹{normal_total:,.0f}**"
        )

        st.write(
            f"**Total making cost: ₹{total_cost:,.0f}**"
        )

        # ------------------------------------------
        # ACTUAL AMOUNT PAID
        # ------------------------------------------

        amount_paid = st.number_input(
            "Amount actually paid by customer (₹)",
            min_value=0.0,
            value=float(normal_total),
            step=1.0
        )

        discount = normal_total - amount_paid

        if discount > 0:

            st.info(
                f"Discount / reduction given: "
                f"₹{discount:,.0f}"
            )

        elif discount < 0:

            st.info(
                f"Customer paid ₹"
                f"{abs(discount):,.0f} more than "
                f"the normal total."
            )

        actual_profit = amount_paid - total_cost

        st.metric(
            "Profit from this order",
            f"₹{actual_profit:,.0f}"
        )

        # ------------------------------------------
        # SAVE ORDER
        # ------------------------------------------

        if st.button(
            "💾 Save entire order",
            use_container_width=True
        ):

            if amount_paid <= 0:

                st.error(
                    "Amount paid must be greater than ₹0."
                )

            else:

                # Store all items in one text field
                details = " | ".join(
                    [
                        f"{x['product']} × {x['quantity']}"
                        for x in st.session_state.order_items
                    ]
                )

                # Store the order as ONE sales record
                sb.table("sales").insert({
                    "date": today,
                    "product": "Order",
                    "quantity": total_quantity,
                    "sales": amount_paid,
                    "profit": actual_profit,
                    "customer_name": customer_name.strip(),
                    "order_details": details
                }).execute()

                st.session_state.order_items = []
                st.session_state.order_customer = ""

                st.success(
                    "Order saved successfully."
                )

                st.rerun()

        # ------------------------------------------
        # CLEAR ORDER
        # ------------------------------------------

        if st.button(
            "Clear current order",
            use_container_width=True
        ):

            st.session_state.order_items = []
            st.session_state.order_customer = ""

            st.rerun()

    else:

        st.info(
            "No items added yet. Choose a product or "
            "combo and click Add to order."
        )

# ==================================================
# PURCHASE
# ==================================================

elif page == "Purchase":

    st.markdown(
        '<div class="section">Add ingredient purchase</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Enter only what you actually spent buying ingredients."
    )

    with st.form("purchase"):

        item = st.text_input(
            "What did you buy?",
            placeholder="Chocolate, butter, cocoa powder..."
        )

        amount = st.number_input(
            "Amount spent (₹)",
            min_value=0.0,
            step=10.0
        )

        if st.form_submit_button(
            "Save purchase",
            use_container_width=True
        ):

            if not item.strip() or amount <= 0:

                st.error(
                    "Enter the item and amount."
                )

            else:

                sb.table("purchases").insert({
                    "date": today,
                    "item": item.strip(),
                    "amount": amount
                }).execute()

                st.success(
                    "Purchase saved to cloud."
                )

                st.rerun()

# ==================================================
# REPORTS
# ==================================================

else:

    st.markdown(
        '<div class="section">Reports</div>',
        unsafe_allow_html=True
    )

    mode = st.radio(
        "Period",
        ["This month", "All time", "Custom"],
        horizontal=True
    )

    start = end = None

    if mode == "This month":

        start, end = month, today

    elif mode == "Custom":

        a, b = st.columns(2)

        with a:
            start = st.date_input(
                "From",
                date.today().replace(day=1)
            ).isoformat()

        with b:
            end = st.date_input(
                "To",
                date.today()
            ).isoformat()

    sr = filt(sales, start, end)
    pr = filt(purchases, start, end)

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    total_sales = sum(
        float(x["sales"])
        for x in sr
    )

    total_profit = sum(
        float(x["profit"])
        for x in sr
    )

    total_ingredients = sum(
        float(x["amount"])
        for x in pr
    )

    total_items = sum(
        int(x["quantity"])
        for x in sr
    )

    cols = st.columns(4)

    for c, l, v in zip(
        cols,
        [
            "Sales",
            "Profit",
            "Ingredients",
            "Items sold"
        ],
        [
            total_sales,
            total_profit,
            total_ingredients,
            total_items
        ]
    ):

        with c:

            st.metric(
                l,
                f"₹{v:,.0f}"
                if l != "Items sold"
                else f"{v:,.0f}"
            )

    # ----------------------------------------------
    # SALES
    # ----------------------------------------------

    st.markdown(
        '<div class="section">Sales</div>',
        unsafe_allow_html=True
    )

    if not sr:

        st.info("No sales for this period.")

    for r in sr:

        customer = (
            r.get("customer_name", "")
            or ""
        ).strip()

        details = (
            r.get("order_details", "")
            or ""
        ).strip()

        c1, c2, c3, c4, c5, c6 = st.columns(
            [1.2, 2.8, 1, 1, 1, .8]
        )

        c1.write(
            str(r["date"])[:10]
        )

        if customer:

            c2.write(
                f"👤 **{customer}**"
            )

            if details:
                c2.caption(details)

        else:

            c2.write(
                details if details else r["product"]
            )

        c3.write(
            f"× {r['quantity']}"
        )

        c4.write(
            f"₹{float(r['sales']):,.0f}"
        )

        c5.write(
            f"₹{float(r['profit']):,.0f}"
        )

        if c6.button(
            "🗑️",
            key=f"d{r['id']}"
        ):

            sb.table("sales") \
                .delete() \
                .eq("id", r["id"]) \
                .execute()

            st.rerun()

    # ----------------------------------------------
    # PURCHASES
    # ----------------------------------------------

    st.markdown(
        '<div class="section">Ingredient purchases</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        [
            {
                "Date": str(r["date"])[:10],
                "Item": r["item"],
                "Amount (₹)": r["amount"]
            }
            for r in pr
        ],
        use_container_width=True
    )

    # ----------------------------------------------
    # PRODUCTS
    # ----------------------------------------------

    st.markdown(
        '<div class="section">Products</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        [
            {
                "Product": p,
                "Selling Price (₹)": v[0],
                "Profit (₹)": v[1]
            }
            for p, v in PRODUCTS.items()
        ],
        use_container_width=True
    )

    # ----------------------------------------------
    # COMBOS
    # ----------------------------------------------

    st.markdown(
        '<div class="section">Temporary combos</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        [
            {
                "Combo": name,
                "Customer Price (₹)": values[0],
                "Making Cost (₹)": values[1],
                "Profit (₹)": values[0] - values[1]
            }
            for name, values in COMBOS.items()
        ],
        use_container_width=True
    )

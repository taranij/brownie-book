import streamlit as st
from datetime import date
from supabase import create_client

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Brownie Book 🍫",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SUPABASE
# =========================================================

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================================================
# PRODUCTS
# selling price, profit
# =========================================================

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

# =========================================================
# COMBOS
#
# 299 Combo:
# Advertised/value name = 299 Combo
# Actual customer payment = ₹259
# Making cost = ₹100
# Actual profit = ₹159
# =========================================================

COMBOS = {
    "299 Combo": (259, 100)
}

# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "order_items" not in st.session_state:
    st.session_state.order_items = []

if "order_customer" not in st.session_state:
    st.session_state.order_customer = ""

# =========================================================
# HELPERS
# =========================================================

def go(page):
    st.session_state.page = page
    st.rerun()


def money(value):
    return f"₹{float(value):,.0f}"


def filt(rows, start=None, end=None):
    return [
        r for r in rows
        if (not start or str(r["date"])[:10] >= start)
        and (not end or str(r["date"])[:10] <= end)
    ]


def load_data():

    sales = (
        sb.table("sales")
        .select("*")
        .order("id", desc=True)
        .execute()
        .data
        or []
    )

    purchases = (
        sb.table("purchases")
        .select("*")
        .order("id", desc=True)
        .execute()
        .data
        or []
    )

    return sales, purchases


def add_order_item(name, price, cost, qty):

    st.session_state.order_items.append({
        "product": name,
        "quantity": int(qty),
        "price": float(price),
        "cost": float(cost)
    })


def clear_order():

    st.session_state.order_items = []
    st.session_state.order_customer = ""


# =========================================================
# CLEAN UI
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background-color: #faf8f6;
}

.block-container {
    max-width: 1150px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

/* Main title */

.main-title {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #351d14;
}

.main-subtitle {
    color: #806d63;
    margin-top: -8px;
    margin-bottom: 20px;
}

/* Section headings */

.section-heading {
    font-size: 1.35rem;
    font-weight: 750;
    color: #382118;
    margin-top: 1.2rem;
    margin-bottom: .25rem;
}

.section-caption {
    color: #88766e;
    font-size: .9rem;
    margin-bottom: .8rem;
}

/* Metric cards */

.metric-box {
    background: white;
    border: 1px solid #eadfd9;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(70,40,25,.05);
}

.metric-icon {
    font-size: 1.3rem;
}

.metric-label {
    color: #806d63;
    font-size: .82rem;
    margin-top: 5px;
}

.metric-number {
    color: #321b12;
    font-size: 1.55rem;
    font-weight: 750;
    margin-top: 2px;
}

/* Order cards */

.order-box {
    background: white;
    border: 1px solid #eadfd9;
    border-radius: 17px;
    padding: 14px 16px;
    margin-bottom: 8px;
}

.order-customer {
    font-weight: 700;
    color: #3b2319;
}

.order-details {
    color: #77665e;
    font-size: .85rem;
    margin-top: 4px;
}

.order-money {
    font-weight: 750;
    color: #5a2e1d;
}

.order-profit {
    color: #47704f;
    font-size: .82rem;
    font-weight: 600;
}

/* Buttons */

.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 650;
}

/* Mobile */

@media (max-width: 700px) {

    .block-container {
        padding-left: .7rem;
        padding-right: .7rem;
    }

    .main-title {
        font-size: 1.8rem;
    }

    .metric-box {
        padding: 13px;
    }

    .metric-number {
        font-size: 1.25rem;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🍫 Brownie Book</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Your little business, beautifully organised.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# NAVIGATION
# =========================================================

nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:
    if st.button("🏠 Dashboard", use_container_width=True):
        go("Dashboard")

with nav2:
    if st.button("➕ Add Sale", use_container_width=True):
        go("Add Sale")

with nav3:
    if st.button("🛒 Purchase", use_container_width=True):
        go("Purchase")

with nav4:
    if st.button("📊 Reports", use_container_width=True):
        go("Reports")

st.divider()

# =========================================================
# DATA
# =========================================================

today = date.today().isoformat()
month = date.today().replace(day=1).isoformat()

sales, purchases = load_data()

page = st.session_state.page

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    month_sales = filt(sales, month, today)
    month_purchases = filt(purchases, month, today)

    total_sales = sum(
        float(x["sales"]) for x in month_sales
    )

    total_profit = sum(
        float(x["profit"]) for x in month_sales
    )

    ingredient_spend = sum(
        float(x["amount"]) for x in month_purchases
    )

    total_items = sum(
        int(x["quantity"]) for x in month_sales
    )

    st.markdown(
        '<div class="section-heading">'
        'Good to see you 👋'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Here is how your brownie business is doing this month.'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------- METRICS ----------------

    metric_cols = st.columns(2)

    metrics = [
        ("💰", "Sales", money(total_sales)),
        ("📈", "Profit", money(total_profit)),
        ("🛒", "Ingredients", money(ingredient_spend)),
        ("📦", "Items sold", f"{total_items:,}")
    ]

    for i, (icon, label, value) in enumerate(metrics):

        with metric_cols[i % 2]:

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-number">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if i % 2 == 1:
            st.write("")

    # ---------------- QUICK ACTIONS ----------------

    st.markdown(
        '<div class="section-heading">'
        'Quick actions'
        '</div>',
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    with a:
        if st.button(
            "➕ Create New Order",
            use_container_width=True
        ):
            go("Add Sale")

    with b:
        if st.button(
            "🛒 Record Purchase",
            use_container_width=True
        ):
            go("Purchase")

    # ---------------- RECENT ORDERS ----------------

    st.markdown(
        '<div class="section-heading">'
        'Recent orders'
        '</div>',
        unsafe_allow_html=True
    )

    if not sales:

        st.info(
            "🍫 No orders yet. Your first sale will appear here."
        )

    else:

        for r in sales[:8]:

            customer = (
                r.get("customer_name", "")
                or ""
            ).strip()

            details = (
                r.get("order_details", "")
                or ""
            ).strip()

            customer = customer or "Walk-in / No name"

            details = details or r.get(
                "product",
                "Order"
            )

            c1, c2 = st.columns([4, 1])

            with c1:

                st.markdown(
                    f"""
                    <div class="order-box">

                        <div class="order-customer">
                            👤 {customer}
                        </div>

                        <div class="order-details">
                            {details}
                        </div>

                        <div class="order-details">
                            📅 {str(r["date"])[:10]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                st.write("")

                st.markdown(
                    f"""
                    <div style="text-align:right">

                        <div class="order-money">
                            {money(r["sales"])}
                        </div>

                        <div class="order-profit">
                            +{money(r["profit"])} profit
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =========================================================
# ADD SALE
# =========================================================

elif page == "Add Sale":

    st.markdown(
        '<div class="section-heading">'
        'Create an order ✨'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Add everything the customer ordered in one place.'
        '</div>',
        unsafe_allow_html=True
    )

    # CUSTOMER

    customer_name = st.text_input(
        "Customer name",
        value=st.session_state.order_customer,
        placeholder="Optional — e.g. Priya"
    )

    st.session_state.order_customer = customer_name

    # ITEM TYPE

    st.markdown(
        '<div class="section-heading">'
        'Add items'
        '</div>',
        unsafe_allow_html=True
    )

    item_type = st.radio(
        "What are you adding?",
        ["🍫 Product", "🎁 Combo"],
        horizontal=True
    )

    # ---------------- PRODUCT ----------------

    if item_type == "🍫 Product":

        selected = st.selectbox(
            "Select product",
            list(PRODUCTS.keys())
        )

        price, normal_profit = PRODUCTS[selected]

        cost = price - normal_profit

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.info(
            f"{selected}  •  "
            f"{money(price)} each  •  "
            f"{money(normal_profit)} profit each"
        )

    # ---------------- COMBO ----------------

    else:

        selected = st.selectbox(
            "Select combo",
            list(COMBOS.keys())
        )

        price, cost = COMBOS[selected]

        normal_profit = price - cost

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.info(
            f"{selected}  •  "
            f"Customer price {money(price)}  •  "
            f"Making cost {money(cost)}  •  "
            f"Profit {money(normal_profit)}"
        )

    # ADD ITEM

    if st.button(
        "➕ Add to Order",
        use_container_width=True
    ):

        add_order_item(
            selected,
            price,
            cost,
            qty
        )

        st.success(
            f"{selected} × {qty} added to order."
        )

    # =====================================================
    # CURRENT ORDER
    # =====================================================

    if st.session_state.order_items:

        st.markdown(
            '<div class="section-heading">'
            'Current order 🧾'
            '</div>',
            unsafe_allow_html=True
        )

        normal_total = 0
        total_cost = 0
        total_quantity = 0

        for i, item in enumerate(
            st.session_state.order_items
        ):

            line_total = (
                item["price"] *
                item["quantity"]
            )

            line_cost = (
                item["cost"] *
                item["quantity"]
            )

            normal_total += line_total
            total_cost += line_cost
            total_quantity += item["quantity"]

            c1, c2, c3 = st.columns([5, 2, 1])

            with c1:

                st.write(
                    f"**{item['product']}**"
                )

                st.caption(
                    f"Qty: {item['quantity']} "
                    f"• Cost: {money(line_cost)}"
                )

            with c2:

                st.write(
                    f"**{money(line_total)}**"
                )

            with c3:

                if st.button(
                    "✕",
                    key=f"remove_{i}"
                ):

                    st.session_state.order_items.pop(i)
                    st.rerun()

        st.divider()

        # ORDER TOTAL

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Normal total",
                money(normal_total)
            )

        with col2:

            st.metric(
                "Making cost",
                money(total_cost)
            )

        # PAYMENT

        st.markdown(
            '<div class="section-heading">'
            'Payment 💳'
            '</div>',
            unsafe_allow_html=True
        )

        amount_paid = st.number_input(
            "Amount actually paid",
            min_value=0.0,
            value=float(normal_total),
            step=1.0
        )

        discount = normal_total - amount_paid

        actual_profit = amount_paid - total_cost

        if discount > 0:

            st.warning(
                f"🏷️ Discount given: {money(discount)}"
            )

        elif discount == 0:

            st.success(
                "No discount — customer paid the normal total."
            )

        else:

            st.info(
                f"Customer paid {money(abs(discount))} "
                "more than the normal total."
            )

        st.metric(
            "Actual profit from this order",
            money(actual_profit)
        )

        # SAVE

        if st.button(
            "💾 Save Order",
            use_container_width=True,
            type="primary"
        ):

            if amount_paid <= 0:

                st.error(
                    "Amount paid must be greater than ₹0."
                )

            else:

                details = " | ".join(
                    [
                        f"{x['product']} × {x['quantity']}"
                        for x in st.session_state.order_items
                    ]
                )

                sb.table("sales").insert({
                    "date": today,
                    "product": "Order",
                    "quantity": total_quantity,
                    "sales": amount_paid,
                    "profit": actual_profit,
                    "customer_name": customer_name.strip(),
                    "order_details": details
                }).execute()

                clear_order()

                st.success(
                    "🎉 Order saved successfully!"
                )

                st.rerun()

        if st.button(
            "Clear Order",
            use_container_width=True
        ):

            clear_order()
            st.rerun()

    else:

        st.info(
            "🧾 Your order is empty. Add a product or combo above."
        )


# =========================================================
# PURCHASE
# =========================================================

elif page == "Purchase":

    st.markdown(
        '<div class="section-heading">'
        'Ingredient spending 🛒'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Record what you actually spent buying ingredients."
    )

    with st.form("purchase"):

        item = st.text_input(
            "What did you buy?",
            placeholder="Chocolate, butter, cocoa powder..."
        )

        amount = st.number_input(
            "Amount spent",
            min_value=0.0,
            step=10.0
        )

        submitted = st.form_submit_button(
            "💾 Save Purchase",
            use_container_width=True
        )

        if submitted:

            if not item.strip() or amount <= 0:

                st.error(
                    "Please enter the item and amount."
                )

            else:

                sb.table("purchases").insert({
                    "date": today,
                    "item": item.strip(),
                    "amount": amount
                }).execute()

                st.success(
                    "🛒 Purchase saved."
                )

                st.rerun()


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.markdown(
        '<div class="section-heading">'
        'Reports 📊'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Review your sales, profits and spending."
    )

    mode = st.radio(
        "Period",
        ["This month", "All time", "Custom"],
        horizontal=True
    )

    start = None
    end = None

    if mode == "This month":

        start = month
        end = today

    elif mode == "Custom":

        c1, c2 = st.columns(2)

        with c1:

            start = st.date_input(
                "From",
                date.today().replace(day=1)
            ).isoformat()

        with c2:

            end = st.date_input(
                "To",
                date.today()
            ).isoformat()

    sr = filt(sales, start, end)
    pr = filt(purchases, start, end)

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

    # ---------------- REPORT METRICS ----------------

    m1, m2 = st.columns(2)

    with m1:
        st.metric(
            "💰 Sales",
            money(total_sales)
        )

    with m2:
        st.metric(
            "📈 Profit",
            money(total_profit)
        )

    m3, m4 = st.columns(2)

    with m3:
        st.metric(
            "🛒 Ingredients",
            money(total_ingredients)
        )

    with m4:
        st.metric(
            "📦 Items",
            f"{total_items:,}"
        )

    # =====================================================
    # ORDERS
    # =====================================================

    st.markdown(
        '<div class="section-heading">'
        'Orders'
        '</div>',
        unsafe_allow_html=True
    )

    if not sr:

        st.info(
            "📭 No orders found for this period."
        )

    else:

        for r in sr:

            customer = (
                r.get("customer_name", "")
                or ""
            ).strip()

            details = (
                r.get("order_details", "")
                or ""
            ).strip()

            customer = customer or "Walk-in / No name"

            details = details or r.get(
                "product",
                "Order"
            )

            with st.container(border=True):

                c1, c2 = st.columns([5, 1])

                with c1:

                    st.write(
                        f"👤 **{customer}**"
                    )

                    st.caption(
                        f"{details}  •  "
                        f"{str(r['date'])[:10]}"
                    )

                with c2:

                    st.write(
                        f"**{money(r['sales'])}**"
                    )

                    st.caption(
                        f"+{money(r['profit'])} profit"
                    )

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{r['id']}"
                ):

                    sb.table("sales") \
                        .delete() \
                        .eq("id", r["id"]) \
                        .execute()

                    st.success(
                        "Order deleted."
                    )

                    st.rerun()

    # =====================================================
    # PURCHASES
    # =====================================================

    st.markdown(
        '<div class="section-heading">'
        'Ingredient purchases'
        '</div>',
        unsafe_allow_html=True
    )

    if pr:

        for r in pr:

            with st.container(border=True):

                c1, c2 = st.columns([4, 1])

                with c1:

                    st.write(
                        f"🛒 **{r['item']}**"
                    )

                    st.caption(
                        str(r["date"])[:10]
                    )

                with c2:

                    st.write(
                        f"**{money(r['amount'])}**"
                    )

    else:

        st.info(
            "No ingredient purchases recorded."
        )

    # =====================================================
    # PRODUCT REFERENCE
    # =====================================================

    st.markdown(
        '<div class="section-heading">'
        'Product reference'
        '</div>',
        unsafe_allow_html=True
    )

    product_rows = []

    for name, (price, profit) in PRODUCTS.items():

        cost = price - profit

        product_rows.append({
            "Product": name,
            "Selling Price": money(price),
            "Making Cost": money(cost),
            "Profit": money(profit)
        })

    st.dataframe(
        product_rows,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # COMBO REFERENCE
    # =====================================================

    st.markdown(
        '<div class="section-heading">'
        'Combo reference 🎁'
        '</div>',
        unsafe_allow_html=True
    )

    combo_rows = []

    for name, (price, cost) in COMBOS.items():

        combo_rows.append({
            "Combo": name,
            "Customer Pays": money(price),
            "Making Cost": money(cost),
            "Profit": money(price - cost)
        })

    st.dataframe(
        combo_rows,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🍫 Brownie Book • Your business, your numbers."
)

# Sprint 2 — Recommendation Engine, Analysis Pages & Charts

> **Goal**: The core product — users get personalized card recommendations with explanations and interactive charts.
> **Core Req points targeted**: UI #4 Dashboard (50 pts) + #5 Analysis Informed Decision (25 pts) + #6 Analysis Current Data (25 pts) + Charting (75 pts)
> **Prerequisites**: Sprint 1 completed (auth + ingestion working). Read `MASTER.md`.

---

## Context

Read `prompts/MASTER.md` for the recommendation engine algorithm, schema, and conventions. Users can already register, log in, and upload transactions (Sprint 1). This sprint builds the intelligence layer.

---

## Tasks

### Task 2.1 — Recommendation Engine Service

**File**: `app/services/recommendation_engine.py`

Implement the core algorithm from MASTER.md. The service should be a pure calculation module — no Flask dependencies, no route logic. This makes it testable in isolation.

```python
class RecommendationEngine:
    def __init__(self, cards: list[Card], transactions: list[Transaction], preferences: dict):
        """
        Args:
            cards: list of Card model objects from DB
            transactions: user's imported transactions
            preferences: {
                'mode': 'travel' | 'cashback',
                'preferred_partners': ['hyatt', 'united'],
                'fee_tolerance': 550,
                'cpp_override': 1.5  # optional cents-per-point override
            }
        """
        self.cards = cards
        self.transactions = transactions
        self.preferences = preferences

    def compute_annual_spend_by_category(self) -> dict:
        """Aggregate transactions → { 'dining': 9600, 'groceries': 7200, ... }
        Annualize if < 12 months of data (extrapolate proportionally)."""
        ...

    def compute_card_value(self, card: Card, spend_by_cat: dict) -> dict:
        """
        For one card, compute:
        - gross_reward_value: Σ(category_spend × multiplier × point_value)
        - credits_value: Σ(credit × utilization_rate)
        - annual_fee: card.annual_fee
        - net_value: gross - fee + credits
        - drivers: top 3 contributing categories with dollar amounts
        - break_even_monthly: annual_fee / 12 ... monthly spend needed to justify fee
        Returns dict with all above fields.
        """
        ...

    def recommend(self) -> list[dict]:
        """
        Compute net value for every card, filter by fee_tolerance,
        sort descending, return top 3 with full breakdown.
        Each result dict:
        {
            'card_id': str,
            'card_name': str,
            'net_value': float,
            'gross_value': float,
            'annual_fee': float,
            'credits_value': float,
            'drivers': [{'category': str, 'contribution': float, 'multiplier': float}, ...],
            'break_even_monthly_spend': float,
            'rank': int
        }
        """
        ...
```

**Critical edge cases to handle**:
- User has 0 transactions → return empty result with explanation
- User has < 1 month of data → warn about extrapolation uncertainty
- Card has no bonus for user's top categories → still compute at base rate
- Category cap exceeded → cap the bonus spending
- Division by zero: if all spend is $0, don't divide

**Test cases** (`tests/test_recommendation.py`):
- Given known transactions + known card → verify exact net_value calculation
- Given dining-heavy spender → Amex Gold should rank higher than Citi Double Cash
- Given low spender → $0 fee cards should beat high-fee cards
- Given fee_tolerance = 0 → only $0 fee cards returned
- Given 0 transactions → empty result, no crash
- Determinism: same inputs → same output (run twice, compare)

### Task 2.2 — Dashboard Full Implementation (Screen #4, 50 pts)

**Route**: `GET /dashboard`

**Requirements**:
- Must be **visually distinct** from the unauthenticated home page
- Show welcome: "Welcome back, {display_name}"
- **Data Summary Panel** (if user has transactions):
  - Total transactions imported
  - Date range of data
  - Total spend amount
  - Top 3 categories by spend (with amounts)
- **Quick Recommendation Preview** (if user has run a recommendation):
  - Top recommended card name + estimated value
  - Link to full analysis
- **Action Cards**:
  - "Upload Transactions" → /ingestion
  - "Run Recommendation" → /analysis/decision
  - "View History" → /history
- **If no data**: show a prominent "Get Started" section guiding user to upload first

### Task 2.3 — Analysis: Informed Decision (Screen #5, 25 pts)

**Route**: `GET /analysis/decision`, `POST /analysis/decision/run`

This is the MOST IMPORTANT screen — it's where the user makes the "buy/sell" decision.

**Requirements**:

**Preferences Panel (top)**:
- Dropdown: Travel vs Cash-back mode
- Multi-select: Preferred transfer partners (Hyatt, United, Southwest, etc.)
- Slider: Annual fee tolerance ($0 – $700)
- Slider: Cents per point override (0.5 – 3.0 cpp, step 0.1)
- Button: "Generate Recommendations"

**Results Panel (middle)**:
- Show top 3 cards side-by-side in card-like UI:
  - Card name + issuer logo (or placeholder)
  - Annual fee
  - Estimated net annual value (BIG number, prominent)
  - Top 3 drivers with dollar amounts
  - Break-even monthly spend
- Highlight #1 with a "Best Pick" badge

**Explanation Panel (below cards)**:
- Natural-language explanation: "Based on your $9,600/yr dining spend, the Amex Gold's 4x multiplier earns you $384 more than a flat 2% card. Combined with $240 in credits..."
- Show assumptions used (cpp value, partner valuations)

**Charts (right side or below)** — see Task 2.5

**Action Buttons**:
- "Commit This Plan" → POST /plan/commit (Sprint 3, but the button should exist)
- "Adjust Assumptions" → scrolls to preferences panel

**Backend logic**:
1. On POST, run `RecommendationEngine.recommend()`
2. Store result as `RecommendationRun` in DB
3. Create SystemEvent: type='rec_run'
4. Return results to template (or as JSON for AJAX)

**AJAX approach (recommended for interactivity)**:
- When user adjusts cpp slider or partner selection, fire AJAX POST with updated preferences
- Backend recomputes, returns JSON
- Frontend JS updates cards + charts without full page reload

### Task 2.4 — Analysis: Current Data (Screen #6, 25 pts)

**Route**: `GET /analysis/current`

**Requirements**:
- **Spend by Category** — bar chart (see Task 2.5)
- **Monthly Spending Trend** — line chart
- **Summary Stats Table**:
  - Total spend (annualized)
  - Average monthly spend
  - Highest category + % of total
  - Number of transactions
  - Date range
- **Current Cards** (if user has committed plans):
  - Show which cards user has "applied" (from PlanCommit)
  - Show estimated captured value vs. potential value (gap analysis)
- Link to "Run Recommendation" if user hasn't run one yet

### Task 2.5 — Charting with Plotly.js (75 pts)

Must implement **3 chart types** + at least **1 custom interaction**.

**Chart 1: Bar Chart — Spend by Category**
- Location: Analysis Current Data page (Screen #6)
- X-axis: categories (dining, groceries, travel, ...)
- Y-axis: annualized spend ($)
- Color-coded bars
- Hover: show exact amount + % of total

```javascript
// static/js/charts.js
function renderSpendByCategory(data) {
    // data = [{category: 'dining', amount: 9600}, ...]
    const trace = {
        x: data.map(d => d.category),
        y: data.map(d => d.amount),
        type: 'bar',
        marker: { color: ['#FF6384', '#36A2EB', '#FFCE56', ...] },
        hovertemplate: '%{x}: $%{y:,.0f} (%{customdata:.1f}%)<extra></extra>',
        customdata: data.map(d => d.pct)
    };
    Plotly.newPlot('chart-spend-category', [trace], {
        title: 'Annual Spend by Category',
        yaxis: { title: 'Amount ($)', tickprefix: '$' }
    });
}
```

**Chart 2: Line Chart — Monthly Spend Trend / Cumulative Rewards Value**
- Location: Analysis Current Data page AND/OR Informed Decision page
- X-axis: month (Sep 2025, Oct 2025, ...)
- Y-axis: monthly spend OR cumulative rewards value
- Multiple lines if comparing cards

```javascript
function renderMonthlyTrend(months, spendData) {
    const trace = {
        x: months,
        y: spendData,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Monthly Spend'
    };
    Plotly.newPlot('chart-monthly-trend', [trace], {
        title: 'Monthly Spending Trend',
        yaxis: { title: 'Amount ($)', tickprefix: '$' }
    });
}
```

**Chart 3: Scatter Plot — Effective Reward Rate vs Annual Fee**
- Location: Analysis Informed Decision page
- X-axis: annual fee ($)
- Y-axis: effective reward rate (%) or net annual value ($)
- Each dot = a card in the catalog
- Top 3 recommended cards highlighted (larger dots, different color)
- Hover: card name + net value

```javascript
function renderCardScatter(cards, recommended) {
    const allCards = {
        x: cards.map(c => c.annual_fee),
        y: cards.map(c => c.net_value),
        text: cards.map(c => c.name),
        type: 'scatter',
        mode: 'markers',
        marker: { size: 8, color: '#ccc' },
        name: 'All Cards'
    };
    const topCards = {
        x: recommended.map(c => c.annual_fee),
        y: recommended.map(c => c.net_value),
        text: recommended.map(c => c.name),
        type: 'scatter',
        mode: 'markers+text',
        textposition: 'top center',
        marker: { size: 14, color: '#FF6384' },
        name: 'Recommended'
    };
    Plotly.newPlot('chart-card-scatter', [allCards, topCards], {
        title: 'Card Value vs Annual Fee',
        xaxis: { title: 'Annual Fee ($)', tickprefix: '$' },
        yaxis: { title: 'Net Annual Value ($)', tickprefix: '$' }
    });
}
```

**Custom Interaction (REQUIRED for full marks, −10 pts if missing):**

Implement a **CPP (cents-per-point) slider** that dynamically updates:
- The recommendation ranking
- All three charts
- The explanation panel

```javascript
// static/js/slider.js
const cppSlider = document.getElementById('cpp-slider');
const cppValue = document.getElementById('cpp-value');

cppSlider.addEventListener('input', function() {
    cppValue.textContent = this.value + ' cpp';
    // Debounce, then fire AJAX
    clearTimeout(window._sliderTimeout);
    window._sliderTimeout = setTimeout(() => {
        fetch('/analysis/decision/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpp_override: parseFloat(this.value),
                mode: document.getElementById('mode-select').value,
                preferred_partners: getSelectedPartners()
            })
        })
        .then(r => r.json())
        .then(data => {
            updateCards(data.recommendations);
            renderCardScatter(data.all_cards, data.recommendations);
            renderSpendByCategory(data.spend_by_category);
            // ... update other elements
        });
    }, 300);
});
```

### Task 2.6 — API Endpoint for AJAX Recommendation

**Route**: `POST /api/recommend` (JSON API)

```python
@analysis_bp.route('/api/recommend', methods=['POST'])
@login_required
def api_recommend():
    data = request.get_json()
    prefs = {
        'mode': data.get('mode', current_user.preference_mode),
        'preferred_partners': data.get('preferred_partners', current_user.preferred_partners),
        'fee_tolerance': data.get('fee_tolerance', current_user.fee_tolerance),
        'cpp_override': data.get('cpp_override', 1.5)
    }
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    cards = Card.query.filter_by(is_active=True).all()
    engine = RecommendationEngine(cards, transactions, prefs)
    results = engine.recommend()
    spend_by_cat = engine.compute_annual_spend_by_category()

    # Save run
    run = RecommendationRun(
        user_id=current_user.id,
        preferences_snapshot=prefs,
        results=results,
        top_card_id=results[0]['card_id'] if results else None,
        total_estimated_value=results[0]['net_value'] if results else 0,
        cpp_assumption=prefs['cpp_override']
    )
    db.session.add(run)
    # ... add SystemEvent
    db.session.commit()

    return jsonify({
        'recommendations': results,
        'spend_by_category': [{'category': k, 'amount': v, 'pct': ...} for k, v in spend_by_cat.items()],
        'run_id': run.run_id
    })
```

---

## Definition of Done (Sprint 2)

- [ ] Recommendation engine produces correct, deterministic results
- [ ] Dashboard shows spend summary and recommendation preview
- [ ] Analysis: Informed Decision shows top 3 cards with explanation
- [ ] Analysis: Current Data shows spend breakdown and trends
- [ ] Bar chart (spend by category) renders with Plotly.js
- [ ] Line chart (monthly trend) renders with Plotly.js
- [ ] Scatter plot (card value vs fee) renders with Plotly.js
- [ ] CPP slider dynamically updates recommendations + charts via AJAX
- [ ] RecommendationRun records saved to DB
- [ ] All tests pass including recommendation engine edge cases
- [ ] Code committed to GitLab

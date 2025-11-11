# Test Case: Personal Expense Tracker

**Recommendation**: A simple personal expense tracker with budget management.

## Why This Works Well

1. **Clear Business Outcomes**: Budget tracking, spending visibility, financial planning
2. **Multiple Specifications**: Validation rules, calculation logic, categorization, date handling
3. **Testable Logic**: Pure functions, edge cases, business rules
4. **Simple But Not Trivial**: ~200-300 lines, 8-10 functions
5. **Realistic O→S→T→C Chains**: Each outcome drives multiple specs, each spec has tests and implementation

---

## Program Overview

```python
# src/expense_tracker.py
"""
Simple expense tracking with categories and budgets.
Supports adding expenses, calculating totals, and budget warnings.
"""
```

**Core Features**:

- Add expenses with amount, category, date, description
- Define monthly budgets per category
- Calculate spending by category
- Check if over budget
- Get spending summary

---

## GOSTC Structure Preview

### Outcomes (4)

```
O-001: Track personal spending accurately
  "As a user, I need to record every expense so I can see where my money goes"

O-002: Stay within budget limits
  "As a user, I need budget alerts so I can avoid overspending"

O-003: Understand spending patterns
  "As a user, I need spending summaries so I can make informed financial decisions"

O-004: Categorize expenses meaningfully
  "As a user, I need expense categories so I can track spending by type"
```

### Specifications (8)

```
S-001: Expense data validation
  satisfies → O-001
  "Expenses must have: positive amount, valid category, valid date, optional description"

S-002: Category management
  satisfies → O-004
  "Support predefined categories: food, transport, entertainment, utilities, other"

S-003: Expense storage interface
  satisfies → O-001
  "In-memory list for MVP; simple add/list operations"

S-004: Budget definition per category
  satisfies → O-002
  "Each category can have a monthly budget limit (positive number or None)"

S-005: Budget calculation logic
  satisfies → O-002
  "Calculate total spent per category; compare against budget; return status"

S-006: Date range filtering
  satisfies → O-003
  "Filter expenses by date range for monthly summaries"

S-007: Spending aggregation
  satisfies → O-003
  "Sum expenses by category; calculate total spending; return summary dict"

S-008: Budget warning system
  satisfies → O-002
  "Warn when spending exceeds 80% of budget; alert when over budget"
```

### Tests (12-15)

```
T-001: Validate expense with valid data
  validates → S-001
  
T-002: Reject expense with negative amount
  validates → S-001

T-003: Reject expense with invalid category
  validates → S-001, S-002

T-004: Validate date formats
  validates → S-001

T-005: Add and retrieve expenses
  validates → S-003

T-006: Calculate spending for single category
  validates → S-005

T-007: Calculate spending for empty category
  validates → S-005

T-008: Budget status when under budget
  validates → S-005, S-008

T-009: Budget warning at 80% threshold
  validates → S-008

T-010: Budget alert when over budget
  validates → S-008

T-011: Filter expenses by date range
  validates → S-006

T-012: Aggregate spending by category
  validates → S-007

T-013: Handle expenses with no budget set
  validates → S-004, S-005
```

### Code Units (8-10)

```
C-001: validate_expense(amount, category, date, description)
  implements → S-001

C-002: VALID_CATEGORIES (constant)
  implements → S-002

C-003: ExpenseTracker.__init__()
  implements → S-003

C-004: ExpenseTracker.add_expense()
  implements → S-003

C-005: ExpenseTracker.set_budget(category, amount)
  implements → S-004

C-006: ExpenseTracker.get_spending(category, start_date, end_date)
  implements → S-005, S-006

C-007: ExpenseTracker.get_budget_status(category)
  implements → S-005, S-008

C-008: ExpenseTracker.get_summary(start_date, end_date)
  implements → S-007

C-009: ExpenseTracker.list_expenses(category, start_date, end_date)
  implements → S-003, S-006
```

---

## Actual Implementation

```python
# src/expense_tracker.py
from datetime import datetime, date
from typing import Optional, Dict, List
from decimal import Decimal

VALID_CATEGORIES = ["food", "transport", "entertainment", "utilities", "other"]

class ExpenseValidationError(Exception):
    """Raised when expense data is invalid"""
    pass

def validate_expense(
    amount: float,
    category: str,
    date_str: str,
    description: str = ""
) -> Dict:
    """
    Validate expense data and return normalized dict.
    
    Raises ExpenseValidationError if invalid.
    """
    if amount <= 0:
        raise ExpenseValidationError("Amount must be positive")
    
    if category not in VALID_CATEGORIES:
        raise ExpenseValidationError(
            f"Category must be one of {VALID_CATEGORIES}"
        )
    
    try:
        expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ExpenseValidationError(
            "Date must be in YYYY-MM-DD format"
        )
    
    return {
        "amount": Decimal(str(amount)),
        "category": category,
        "date": expense_date,
        "description": description,
    }

class ExpenseTracker:
    """Simple in-memory expense tracker with budget management"""
    
    def __init__(self):
        self.expenses: List[Dict] = []
        self.budgets: Dict[str, Decimal] = {}
    
    def add_expense(
        self,
        amount: float,
        category: str,
        date_str: str,
        description: str = ""
    ) -> None:
        """Add a validated expense to the tracker"""
        expense = validate_expense(amount, category, date_str, description)
        self.expenses.append(expense)
    
    def set_budget(self, category: str, amount: float) -> None:
        """Set monthly budget for a category"""
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        if amount <= 0:
            raise ValueError("Budget must be positive")
        self.budgets[category] = Decimal(str(amount))
    
    def get_spending(
        self,
        category: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate total spending for a category in date range"""
        total = Decimal("0")
        for expense in self.expenses:
            if expense["category"] != category:
                continue
            if start_date and expense["date"] < start_date:
                continue
            if end_date and expense["date"] > end_date:
                continue
            total += expense["amount"]
        return total
    
    def get_budget_status(self, category: str) -> Dict:
        """
        Get budget status for a category.
        
        Returns dict with: spent, budget, percentage, status
        Status: "ok" | "warning" | "over" | "no_budget"
        """
        spent = self.get_spending(category)
        budget = self.budgets.get(category)
        
        if budget is None:
            return {
                "spent": spent,
                "budget": None,
                "percentage": None,
                "status": "no_budget"
            }
        
        percentage = (spent / budget * 100) if budget > 0 else 0
        
        if spent > budget:
            status = "over"
        elif percentage >= 80:
            status = "warning"
        else:
            status = "ok"
        
        return {
            "spent": spent,
            "budget": budget,
            "percentage": float(percentage),
            "status": status
        }
    
    def get_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Get spending summary by category for date range"""
        summary = {cat: Decimal("0") for cat in VALID_CATEGORIES}
        
        for expense in self.expenses:
            if start_date and expense["date"] < start_date:
                continue
            if end_date and expense["date"] > end_date:
                continue
            summary[expense["category"]] += expense["amount"]
        
        return {
            "by_category": summary,
            "total": sum(summary.values())
        }
    
    def list_expenses(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """List expenses with optional filtering"""
        filtered = []
        for expense in self.expenses:
            if category and expense["category"] != category:
                continue
            if start_date and expense["date"] < start_date:
                continue
            if end_date and expense["date"] > end_date:
                continue
            filtered.append(expense)
        return filtered
```

```python
# tests/test_expense_tracker.py
import pytest
from datetime import date
from decimal import Decimal
from src.expense_tracker import (
    ExpenseTracker,
    validate_expense,
    ExpenseValidationError,
    VALID_CATEGORIES
)

class TestExpenseValidation:
    """Tests for S-001: Expense data validation"""
    
    def test_valid_expense(self):
        """T-001: Validate expense with valid data"""
        result = validate_expense(
            amount=50.00,
            category="food",
            date_str="2025-03-15",
            description="Groceries"
        )
        assert result["amount"] == Decimal("50.00")
        assert result["category"] == "food"
        assert result["date"] == date(2025, 3, 15)
        assert result["description"] == "Groceries"
    
    def test_negative_amount(self):
        """T-002: Reject expense with negative amount"""
        with pytest.raises(ExpenseValidationError, match="positive"):
            validate_expense(-10, "food", "2025-03-15")
    
    def test_invalid_category(self):
        """T-003: Reject expense with invalid category"""
        with pytest.raises(ExpenseValidationError, match="Category"):
            validate_expense(50, "invalid", "2025-03-15")
    
    def test_invalid_date_format(self):
        """T-004: Reject invalid date formats"""
        with pytest.raises(ExpenseValidationError, match="YYYY-MM-DD"):
            validate_expense(50, "food", "03/15/2025")

class TestExpenseStorage:
    """Tests for S-003: Expense storage interface"""
    
    def test_add_and_retrieve(self):
        """T-005: Add and retrieve expenses"""
        tracker = ExpenseTracker()
        tracker.add_expense(50, "food", "2025-03-15", "Groceries")
        
        expenses = tracker.list_expenses()
        assert len(expenses) == 1
        assert expenses[0]["amount"] == Decimal("50")

class TestBudgetManagement:
    """Tests for S-004, S-005: Budget management"""
    
    def test_calculate_spending_single_category(self):
        """T-006: Calculate spending for single category"""
        tracker = ExpenseTracker()
        tracker.add_expense(30, "food", "2025-03-15")
        tracker.add_expense(20, "food", "2025-03-16")
        tracker.add_expense(50, "transport", "2025-03-15")
        
        food_spending = tracker.get_spending("food")
        assert food_spending == Decimal("50")
    
    def test_calculate_spending_empty_category(self):
        """T-007: Calculate spending for empty category"""
        tracker = ExpenseTracker()
        spending = tracker.get_spending("food")
        assert spending == Decimal("0")

class TestBudgetAlerts:
    """Tests for S-008: Budget warning system"""
    
    def test_under_budget(self):
        """T-008: Budget status when under budget"""
        tracker = ExpenseTracker()
        tracker.set_budget("food", 100)
        tracker.add_expense(50, "food", "2025-03-15")
        
        status = tracker.get_budget_status("food")
        assert status["status"] == "ok"
        assert status["percentage"] == 50.0
    
    def test_warning_at_80_percent(self):
        """T-009: Budget warning at 80% threshold"""
        tracker = ExpenseTracker()
        tracker.set_budget("food", 100)
        tracker.add_expense(85, "food", "2025-03-15")
        
        status = tracker.get_budget_status("food")
        assert status["status"] == "warning"
    
    def test_over_budget(self):
        """T-010: Budget alert when over budget"""
        tracker = ExpenseTracker()
        tracker.set_budget("food", 100)
        tracker.add_expense(120, "food", "2025-03-15")
        
        status = tracker.get_budget_status("food")
        assert status["status"] == "over"
    
    def test_no_budget_set(self):
        """T-013: Handle expenses with no budget set"""
        tracker = ExpenseTracker()
        tracker.add_expense(50, "food", "2025-03-15")
        
        status = tracker.get_budget_status("food")
        assert status["status"] == "no_budget"

class TestDateFiltering:
    """Tests for S-006: Date range filtering"""
    
    def test_filter_by_date_range(self):
        """T-011: Filter expenses by date range"""
        tracker = ExpenseTracker()
        tracker.add_expense(50, "food", "2025-03-01")
        tracker.add_expense(30, "food", "2025-03-15")
        tracker.add_expense(20, "food", "2025-03-31")
        
        march_spending = tracker.get_spending(
            "food",
            start_date=date(2025, 3, 10),
            end_date=date(2025, 3, 20)
        )
        assert march_spending == Decimal("30")

class TestSpendingSummary:
    """Tests for S-007: Spending aggregation"""
    
    def test_summary_by_category(self):
        """T-012: Aggregate spending by category"""
        tracker = ExpenseTracker()
        tracker.add_expense(50, "food", "2025-03-15")
        tracker.add_expense(30, "transport", "2025-03-15")
        tracker.add_expense(20, "food", "2025-03-16")
        
        summary = tracker.get_summary()
        assert summary["by_category"]["food"] == Decimal("70")
        assert summary["by_category"]["transport"] == Decimal("30")
        assert summary["total"] == Decimal("100")
```

---

## Why This Is Perfect for GOSTC Testing

### 1. **Clear O→S→T→C Chains**

Example chain:

```
O-002: Stay within budget limits
  ↓ satisfies
S-005: Budget calculation logic
  ↓ validates
T-006: Calculate spending for single category
T-007: Calculate spending for empty category
  ↓ covers
C-006: ExpenseTracker.get_spending()

S-008: Budget warning system
  ↓ validates
T-008: Budget status when under budget
T-009: Budget warning at 80% threshold
T-010: Budget alert when over budget
  ↓ covers
C-007: ExpenseTracker.get_budget_status()
```

### 2. **Multiple Specs per Outcome**

- O-001 drives S-001, S-003
- O-002 drives S-004, S-005, S-008
- O-003 drives S-006, S-007

### 3. **Tests Cover Multiple Specs**

- T-003 validates both S-001 and S-002
- T-008/009/010 validate both S-005 and S-008

### 4. **Demonstrates GOSTC Queries**

```bash
# What tests validate budget functionality?
gostc query "from O-002 traverse satisfies.validates"

# What code implements spending tracking?
gostc query "from O-001 traverse satisfies.implements"

# Is get_spending() fully tested?
gostc query "from C-006 traverse covers" --direction reverse

# What breaks if I change validation logic?
gostc impact C-001
```

### 5. **Size: Just Right**

- ~150 lines of implementation
- ~100 lines of tests
- 4 outcomes, 8 specs, 13 tests, 9 code units
- Complex enough to show relationships
- Simple enough to understand quickly

---

## Next Steps for GOSTC Development

1. **Manually create the GOSTC graph** for this project (in markdown files)
2. **Implement basic CLI commands**: `init`, `add`, `show`, `list`, `query`
3. **Test integrity checks**: orphaned nodes, broken links
4. **Test impact analysis**: change C-001, see what tests affected
5. **Bootstrap from pytest**: auto-discover tests, infer T-C edges
6. **Validate against pytest**: compare GOSTC T-C edges with actual coverage

This gives you a realistic, manageable test case that exercises all core GOSTC features without overwhelming complexity.
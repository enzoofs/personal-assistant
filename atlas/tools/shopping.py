"""Shopping list handler for ATLAS."""

import logging

from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.memory.store import (
    add_shopping_item,
    get_shopping_list,
    complete_shopping_item,
    clear_completed_shopping,
)
from atlas.orchestrator import register_tool

logger = logging.getLogger(__name__)


async def handle_shopping_add(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Add items to shopping list."""
    items = intent.parameters.get("items", [])
    category = intent.parameters.get("category", "geral")

    if not items:
        raise ValueError("Nenhum item especificado para adicionar")

    added_items = []
    for item in items:
        if isinstance(item, str) and item.strip():
            item_id = add_shopping_item(item.strip(), category=category)
            added_items.append({"id": item_id, "item": item.strip()})

    if not added_items:
        raise ValueError("Nenhum item válido para adicionar")

    items_text = ", ".join([i["item"] for i in added_items])
    context = f"Adicionado(s) à lista de compras: {items_text}."

    action = ActionResult(
        type="shopping_add",
        details={
            "items": added_items,
            "category": category,
            "count": len(added_items),
        },
    )

    logger.info("Added %d items to shopping list: %s", len(added_items), items_text)
    return context, [action]


async def handle_shopping_list(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """List all shopping items."""
    items = get_shopping_list(include_completed=False)

    if not items:
        context = "Sua lista de compras está vazia."
    else:
        # Group by category
        by_category: dict[str, list] = {}
        for item in items:
            cat = item.get("category", "geral")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        lines = []
        for cat, cat_items in by_category.items():
            lines.append(f"\n**{cat.title()}:**")
            for it in cat_items:
                qty = f" ({it['quantity']})" if it.get("quantity") else ""
                lines.append(f"- {it['item']}{qty}")

        context = f"Lista de compras ({len(items)} itens):" + "".join(lines)

    action = ActionResult(
        type="shopping_list",
        details={
            "items": items,
            "count": len(items),
        },
    )

    return context, [action]


async def handle_shopping_complete(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Mark item as purchased."""
    item_id = intent.parameters.get("item_id")
    item_name = intent.parameters.get("item", "")

    # If no ID provided, try to find by name
    if not item_id and item_name:
        items = get_shopping_list(include_completed=False)
        for it in items:
            if item_name.lower() in it["item"].lower():
                item_id = it["id"]
                item_name = it["item"]
                break

    if not item_id:
        raise ValueError(f"Item '{item_name}' não encontrado na lista de compras")

    success = complete_shopping_item(item_id)
    if not success:
        raise ValueError(f"Item com ID {item_id} não encontrado")

    context = f"Item '{item_name}' marcado como comprado."

    action = ActionResult(
        type="shopping_complete",
        details={
            "item_id": item_id,
            "item": item_name,
        },
    )

    logger.info("Completed shopping item: %s (id=%d)", item_name, item_id)
    return context, [action]


# Register handlers
register_tool(IntentType.SHOPPING_ADD, handle_shopping_add)
register_tool(IntentType.SHOPPING_LIST, handle_shopping_list)
register_tool(IntentType.SHOPPING_COMPLETE, handle_shopping_complete)

"""
Product catalog and history query API routes.
"""

from flask import Blueprint, jsonify, request
from repositories.product_repository import load_dataset

product_bp = Blueprint("product", __name__)


@product_bp.route("/api/products", methods=["GET"])
def get_products():
    """
    Searchable and filterable product history endpoint.
    """
    df = load_dataset()
    if df.empty:
        return jsonify({"products": [], "total": 0})

    search_query = request.args.get("search", "").strip().lower()
    status_filter = request.args.get("status", "").strip()
    category_filter = request.args.get("category", "").strip()
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))

    filtered_df = df.copy()

    if status_filter and status_filter != "ALL":
        filtered_df = filtered_df[filtered_df["compliance_status"] == status_filter]

    if category_filter and category_filter != "ALL":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if search_query:
        mask = (
            filtered_df["product_name"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["id"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["manufacturer"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["violations"].astype(str).str.lower().str.contains(search_query)
        )
        filtered_df = filtered_df[mask]

    total_matches = len(filtered_df)
    paged_df = filtered_df.iloc[offset: offset + limit]

    products_list = paged_df.to_dict(orient="records")
    return jsonify({
        "products": products_list,
        "total": total_matches
    })

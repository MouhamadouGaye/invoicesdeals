@router.post("/invoices/{invoice_id}/edit")
async def update_invoice(
    request: Request,
    invoice_id: int,
    title: str = Form(...),
    client_name: str = Form(...),
    client_email: str = Form(...),
    due_date: str = Form(...),
    contract_text: str = Form(""),
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    form = await request.form()

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.title = title
    invoice.client_name = client_name
    invoice.client_email = client_email
    invoice.due_date = datetime.strptime(due_date, "%Y-%m-%d")
    invoice.contract_text = contract_text
    invoice.status = status

    # Handle deleted items
    deleted_ids = form.getlist("deleted_item_ids[]")
    for del_id in deleted_ids:
        item = db.query(InvoiceItem).filter(InvoiceItem.id == int(del_id), InvoiceItem.invoice_id == invoice.id).first()
        if item:
            db.delete(item)

    # Update or add new items
    ids = form.getlist("item_id[]")
    descriptions = form.getlist("description[]")
    quantities = form.getlist("quantity[]")
    unit_prices = form.getlist("unit_price[]")

    total = 0.0
    for i in range(len(descriptions)):
        item_id = ids[i]
        description = descriptions[i]
        quantity = int(quantities[i])
        unit_price = float(unit_prices[i])
        total += quantity * unit_price

        if item_id:
            item = db.query(InvoiceItem).filter(InvoiceItem.id == int(item_id)).first()
            if item:
                item.description = description
                item.quantity = quantity
                item.unit_price = unit_price
        else:
            new_item = InvoiceItem(
                invoice_id=invoice.id,
                description=description,
                quantity=quantity,
                unit_price=unit_price
            )
            db.add(new_item)

    invoice.amount = total
    db.commit()
    return RedirectResponse(url=f"/invoices", status_code=302)

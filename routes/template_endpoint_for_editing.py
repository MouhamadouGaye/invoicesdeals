@router.get("/invoices/{invoice_id}/edit", response_class=HTMLResponse)
def edit_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()

    html_form = f"""
    <html>
    <head>
        <title>Edit Invoice #{invoice.id}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 2rem;
                background-color: #f9f9f9;
                color: #333;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 2rem;
            }}
     
            input, textarea, select {{
                width: 100%;
                padding: 0.5rem;
                margin-top: 0.3rem;
                margin-bottom: 1rem;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 1rem;
            }}
            .item-row {{
                display: flex;
                gap: 1rem;
                align-items: center;
                justify-content: center
                margin-bottom: 1rem;
                background: #fff;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .item-row > div {{
                flex: 1;
            }}
            .item-row button {{
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
              
                border-radius: 5px;
                cursor: pointer;
            }}
            .item-row button:hover {{
                background-color: #b91c1c;
            }}
            .actions {{
                text-align: right;
                margin-top: 2rem;
            }}
            .actions button {{
                background-color: #2563eb;
                color: white;
                padding: 0.7rem 1.4rem;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1rem;
            }}
            .actions button:hover {{
                background-color: #1e40af;
          
            }}
        </style>
    </head>
    <body>
        <h1>Edit Invoice #{invoice.id}</h1>
        <form method="post" action="/invoices/{invoice.id}/edit">
            <label>Title</label>
            <input type="text" name="title" value="{invoice.title}" required />

            <label>Client Name</label>
            <input type="text" name="client_name" value="{invoice.client_name}" required />

            <label>Client Email</label>
            <input type="email" name="client_email" value="{invoice.client_email}" required />

            <label>Due Date</label>
            <input type="date" name="due_date" value="{invoice.due_date.strftime('%Y-%m-%d')}" required />

            <label>Contract</label>
            <textarea name="contract_text" rows="4">{invoice.contract_text or ''}</textarea>

            <label>Status</label>
            <select name="status" required>
                <option value="draft" {"selected" if invoice.status.value == "draft" else ""}>Draft</option>
                <option value="sent" {"selected" if invoice.status.value == "sent" else ""}>Sent</option>
                <option value="paid" {"selected" if invoice.status.value == "paid" else ""}>Paid</option>
            </select> 

            <h3>Invoice Items</h3>
            <div id="items-container">
            
                <div class="item-row" style="border-bottom: 1px solid gray; padding:10px;">
                
                    <div> 
                      <h3>Description</h3>
                    </div>
                    <div>
                         <h3>Quantity</h3>
                    </div>
                    <div>
                         <h3>Price</h3>
                    </div>
                    
                    <button type="hidden" style="background-color: white"> </button>
    
                </div>
            
                {''.join([f"""
                <div class="item-row">
                    <input type="hidden" name="item_id[]" value="{item.id}" />
                    <div> 
                        <input type="text" name="description[]" value="{item.description}" placeholder="Description"  required />
                    </div>
                    <div>
                        <input type="number" name="quantity[]" value="{item.quantity}"  placeholder="Quantity" required />
                    </div>
                    <div>
                        <input type="number" step="0.01" name="unit_price[]" value="{item.unit_price}" placeholder="Price" required />
                    </div>
                    
                    <button type="button" onclick="removeItem(this)">Delete</button>
    
                </div>""" for item in items])}
            </div>

            <div class="actions">
                <button type="button" onclick="addItem()">Add Item</button>
            </div>

            <div class="actions">
                <button type="submit">Update Invoice</button>
            </div>
        </form>

        <script>
        function addItem() {{
            const container = document.getElementById("items-container");
            const div = document.createElement("div");
            div.classList.add("item-row");
            div.innerHTML = `
                <input type="hidden" name="item_id[]" value="" />
                <div>
                    <input type="text" name="description[]" placeholder="Description" required />
                </div>
                <div>
              
                    <input type="number" name="quantity[]" placeholder="Quantity" required />
                </div>
                <div>
     
                    <input type="number" step="0.01" name="unit_price[]" placeholder="Price" required />
                </div>
                <button type="button" onclick="removeItem(this)">Delete</button>
            `;
            container.appendChild(div);
        }}

        function removeItem(button) {{
            const row = button.closest(".item-row");
            const itemIdInput = row.querySelector('input[name="item_id[]"]');
            if (itemIdInput && itemIdInput.value) {{
                const hidden = document.createElement("input");
                hidden.type = "hidden";
                hidden.name = "deleted_item_ids[]";
                hidden.value = itemIdInput.value;
                document.querySelector("form").appendChild(hidden);
            }}
            row.remove();
        }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_form)

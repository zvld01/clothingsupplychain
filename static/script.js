function showForm(formId) {
    const sections = document.querySelectorAll('.form-section');
    sections.forEach(section => {
        if (section.id === formId) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });

    const responses = document.querySelectorAll('.response');
    responses.forEach(response => {
        if (response.id === formId) {
            response.style.display = 'block';
        } else {
            response.style.display = 'none';
        }
    });
}

function addProduct() {
    const product_id = document.getElementById('addProductId').value;
    const product_type = document.getElementById('addProductType').value;
    fetch('/add_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id, product_type }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('addProductId').value = '';
        document.getElementById('addProductType').value = 'tshirt';
    });
}

function deleteProduct() {
    const product_id = document.getElementById('deleteProductId').value;
    fetch('/delete_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('deleteProductId').value = '';
    });
}

function addTransaction() {
    const product_id = document.getElementById('transactionProductId').value;
    const action = document.getElementById('transactionAction').value;
    const user = document.getElementById('transactionUser').value;
    fetch('/add_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id, action, user }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('transactionProductId').value = '';
        document.getElementById('transactionAction').value = '';
        document.getElementById('transactionUser').value = '';
    });
}

function viewInventory() {
    fetch('/view_inventory')
    .then(response => response.json())
    .then(data => {
        const inventoryTable = document.getElementById('inventory').querySelector('table tbody');
        inventoryTable.innerHTML = '';

        Object.entries(data).forEach(([product_id, details]) => {
            const row = inventoryTable.insertRow();
            row.insertCell().textContent = product_id;
            row.insertCell().textContent = details.details;
            row.insertCell().textContent = details.status;
            row.insertCell().textContent = details.signature;
        });

        document.getElementById('inventory').style.display = 'block';
    });
}

document.getElementById('getProductHistoryForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const product_id = formData.get('product_id');

    fetch('/get_product_history?product_id=' + product_id)
    .then(response => response.json())
    .then(data => {
        const historyDiv = document.getElementById('productHistory');
        const table = historyDiv.querySelector('table');
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        data.forEach(transaction => {
            const row = tbody.insertRow();
            row.insertCell().textContent = new Date(transaction.timestamp * 1000).toLocaleString();
            row.insertCell().textContent = transaction.action;
            row.insertCell().textContent = transaction.user;
        });

        table.style.display = 'table';
    });
});

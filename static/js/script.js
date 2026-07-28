// DOM Elements
let openBtn = document.querySelector("#openBtn");
let closeBtn = document.querySelector("#closeBtn");
let modal = document.querySelector("#modal");
let submitBtn = document.querySelector("#log");
let searchInput = document.querySelector("#data");
let searchBtn = document.querySelector("#search");
let hideCodeInput = document.querySelector("#hideCodeInput");
let contactForm = document.querySelector("#contactForm");

let closeView = document.querySelector("#closeView");
let viewModal = document.querySelector("#viewModal");
let userNameSpan = document.querySelector("#userName");
let logoutBtn = document.querySelector("#logoutBtn");

let contacts = [];
let editingContactId = null;
let token = localStorage.getItem('token');

// 1. Authentication Check
if (!token) {
    window.location.href = '/login';
}

// Display logged-in user name
try {
    let savedUser = JSON.parse(localStorage.getItem('user'));
    if (savedUser && savedUser.name) {
        userNameSpan.innerText = savedUser.name;
    }
} catch (e) {}

// Logout handler
logoutBtn.onclick = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
};

// 2. Fetch Contacts from Backend API
async function fetchContacts() {
    let query = searchInput.value.trim();
    let code = hideCodeInput.value.trim();

    let url = '/get';
    if (query || code) {
        url = `/search?q=${encodeURIComponent(query)}&code=${encodeURIComponent(code)}`;
    }

    try {
        let response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }

        let data = await response.json();
        if (response.ok) {
            contacts = data.contacts || [];
            display(contacts);
        } else {
            console.error("Failed to fetch contacts:", data.message);
        }
    } catch (err) {
        console.error("Error fetching contacts:", err);
    }
}

// 3. Display Contacts in DOM
function display(list = contacts) {
    let container = document.querySelector("#cardcontainer");
    document.querySelector("#contactCount").innerText = `Contacts (${list.length})`;

    if (list.length === 0) {
        container.innerHTML = `
            <div class="text-center my-4 text-muted">
                <i class="bi bi-journal-x fs-1"></i>
                <p class="mt-2">No contacts found.</p>
            </div>
        `;
        return;
    }

    // Sort alphabetically by name
    list.sort((a, b) => a.name.localeCompare(b.name));

    let cardHtml = "";
    let currentLetter = "";

    list.forEach((c) => {
        let firstLetter = c.name.charAt(0).toUpperCase();

        if (firstLetter !== currentLetter) {
            cardHtml += `
                <div class="alphabet-heading">
                    ${firstLetter}
                </div>
            `;
            currentLetter = firstLetter;
        }

        cardHtml += `
            <div class="contact-card" onclick="ViewContact(${c.c_id})">
                ${c.image_url
                    ? `<img src="${c.image_url}" class="profile-img" onerror="this.onerror=null;this.src='https://via.placeholder.com/50';">`
                    : `<div class="profile-circle" style="background:${getColor(c.name)};">
                        ${getInitials(c.name)}
                       </div>`
                }

                <div class="contact-info">
                    <h5>${c.name}</h5>
                    <p>${c.relation_profession || c.company_name || c.ph_no || "No details"}</p>
                    ${c.is_hidden ? '<span class="badge bg-warning text-dark mt-1" style="font-size:11px;"><i class="bi bi-lock-fill"></i> Hidden</span>' : ''}
                </div>

                <div class="contact-actions">
                    <button class="icon-btn" onclick="event.stopPropagation(); EditCard(${c.c_id})">
                        <i class="bi bi-pencil-square text-primary"></i>
                    </button>
                    <button class="icon-btn delete" onclick="event.stopPropagation(); DeleteCard(${c.c_id})">
                        <i class="bi bi-trash text-danger"></i>
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = cardHtml;
}

// 4. Modal Handlers
openBtn.onclick = () => {
    editingContactId = null;
    document.querySelector("#modalTitle").innerText = "Add Contact";
    submitBtn.innerText = "Add";
    contactForm.reset();
    modal.style.display = "flex";
};

closeBtn.onclick = () => {
    modal.style.display = "none";
    contactForm.reset();
    editingContactId = null;
};

closeView.onclick = () => {
    viewModal.style.display = "none";
};

// 5. Add / Update Contact API Handler
contactForm.onsubmit = async (event) => {
    event.preventDefault();

    let name = document.querySelector("#name").value.trim();
    let email = document.querySelector("#mail").value.trim();
    let phone = document.querySelector("#phone").value.trim();
    let company = document.querySelector("#company").value.trim();
    let relation = document.querySelector("#relation").value.trim();
    let photoUrl = document.querySelector("#photoUrl").value.trim();
    let hideCode = document.querySelector("#hideCode").value.trim();

    if (!name || !phone) {
        alert("Name and Phone number are required.");
        return;
    }

    let payload = {
        name: name,
        ph_no: phone,
        email: email,
        company_name: company,
        relation_profession: relation,
        image_url: photoUrl,
        hide_code: hideCode
    };

    let url = editingContactId ? `/update/${editingContactId}` : '/create';
    let method = editingContactId ? 'PUT' : 'POST';

    try {
        let response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        let data = await response.json();

        if (response.ok) {
            modal.style.display = "none";
            contactForm.reset();
            editingContactId = null;
            fetchContacts();
        } else {
            alert(data.message || "Failed to save contact.");
        }
    } catch (err) {
        console.error("Error saving contact:", err);
        alert("Server error while saving contact.");
    }
};

// 6. Edit Contact
function EditCard(c_id) {
    let c = contacts.find(item => item.c_id === c_id);
    if (!c) return;

    editingContactId = c_id;
    document.querySelector("#modalTitle").innerText = "Edit Contact";
    submitBtn.innerText = "Update";

    document.querySelector("#name").value = c.name || "";
    document.querySelector("#mail").value = c.email || "";
    document.querySelector("#phone").value = c.ph_no || "";
    document.querySelector("#company").value = c.company_name || "";
    document.querySelector("#relation").value = c.relation_profession || "";
    document.querySelector("#photoUrl").value = c.image_url || "";
    document.querySelector("#hideCode").value = c.hide_code || "";

    modal.style.display = "flex";
}

// 7. View Contact Modal
function ViewContact(c_id) {
    let c = contacts.find(item => item.c_id === c_id);
    if (!c) return;

    let avatar = document.getElementById("viewAvatar");
    if (c.image_url) {
        avatar.innerHTML = `<img src="${c.image_url}" class="view-profile-img rounded-circle mb-3" style="width:80px;height:80px;object-fit:cover;">`;
    } else {
        avatar.innerHTML = `
            <div class="profile-circle large-avatar rounded-circle d-flex align-items-center justify-content-center text-white fw-bold mb-3 mx-auto" style="width:80px;height:80px;background:${getColor(c.name)};font-size:30px;">
                ${getInitials(c.name)}
            </div>
        `;
    }

    document.getElementById("viewName").innerText = c.name;
    document.getElementById("viewEmail").innerText = c.email || "Not Provided";
    document.getElementById("viewPhone").innerText = c.ph_no;
    document.getElementById("viewCompany").innerText = c.company_name || "Not Provided";
    document.getElementById("viewRelation").innerText = c.relation_profession || "Not Provided";

    let hiddenBadge = document.getElementById("viewHiddenBadge");
    if (c.is_hidden) {
        hiddenBadge.style.display = "block";
    } else {
        hiddenBadge.style.display = "none";
    }

    viewModal.style.display = "flex";
}

// 8. Delete Contact API Handler
async function DeleteCard(c_id) {
    if (!confirm("Are you sure you want to delete this contact?")) return;

    try {
        let response = await fetch(`/delete/${c_id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        let data = await response.json();
        if (response.ok) {
            fetchContacts();
        } else {
            alert(data.message || "Failed to delete contact.");
        }
    } catch (err) {
        console.error("Error deleting contact:", err);
    }
}

// 9. Search and Filter Event Listeners
searchInput.addEventListener("input", fetchContacts);
hideCodeInput.addEventListener("input", fetchContacts);
searchBtn.addEventListener("click", fetchContacts);

// Helper functions for Initials & Avatar colors
function getInitials(name) {
    let words = name.trim().split(" ");
    if (words.length === 1) return words[0][0].toUpperCase();
    return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

function getColor(name) {
    const colors = [
        "#7C3AED", "#2563EB", "#059669", "#EA580C",
        "#DB2777", "#0891B2", "#CA8A04", "#4F46E5"
    ];
    let sum = 0;
    for (let i = 0; i < name.length; i++) {
        sum += name.charCodeAt(i);
    }
    return colors[sum % colors.length];
}

// Initial Fetch on Load
fetchContacts();
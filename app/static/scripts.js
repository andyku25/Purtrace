function showPass() {
    let pass_field = document.getElementById("password");
    let icon = document.getElementById("eye");
    if (pass_field.type === 'password') {
        pass_field.type = 'text';
    } else {
        pass_field.type = 'password';
    }
    icon.classList.toggle('fa-eye-slash');
}

function showOther(name) {
    if (name == "Other") {
        document.getElementById("oth-cat").style.display = "block";
    } else {
        document.getElementById("oth-cat").style.display = "none";
    }
}

function editItem() {
    console.log("edit");
    let mod = document.getElementById("mod");
    if (mod.className == "edit") {
        mod.innerHTML = "Save <i class='fa fa-check' aria-hidden='true'></i>";
    } else {
        mod.innerHTML = "Edit <i class='fa fa-pencil' id='pen' aria-hidden='true' style='margin-left: 2px;'></i>";
    }
    mod.classList.toggle('save')
}

function deleteItem() {
    console.log("delete");
}

function displayEdit() {
    let img_container = document.getElementById("edit-img-container");
    img_container.innerHTML = "Edit ";
    img_container.style.display = "block";
}

function editImg() {
    document.getElementById("image").click();
}

function previewImg(upload) {
    document.getElementById("output").src = window.URL.createObjectURL(upload);
}

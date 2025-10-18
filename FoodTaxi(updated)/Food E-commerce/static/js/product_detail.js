const products = document.querySelectorAll(".product");
const overlay = document.getElementById("productOverlay");
const modal = document.getElementById("productModal");
const modalImage = document.getElementById("modalImage");
const modalName = document.getElementById("modalName");
const modalCategory = document.getElementById("modalCategory");
const modalPrice = document.getElementById("modalPrice");
const modalDescription = document.getElementById("modalDescription");
const closeBtn = document.querySelector(".close-btn");
const modalRating = document.getElementById("modalRating");

products.forEach((product) => {
  product.addEventListener("click", () => {
    const img = product.querySelector("img").src;
    const name = product.querySelector(".product-name").textContent;
    const category = product.querySelector(".product-category").textContent;
    const price = product.querySelector(".product-price").textContent;
    const rating = product.querySelector(".product-rating").textContent;

    modalRating.textContent = rating;
    modalImage.src = img;
    modalName.textContent = name;
    modalCategory.textContent = category;
    modalPrice.textContent = price;
    modalDescription.textContent = "This is a placeholder description for now.";

    overlay.classList.add("active");
  });
});

// Close modal when clicking outside or on down arrow
overlay.addEventListener("click", (e) => {
  if (e.target === overlay || e.target === closeBtn) {
    overlay.classList.remove("active");
  }
});

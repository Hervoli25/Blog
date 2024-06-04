document.addEventListener('DOMContentLoaded', () => {
	// Smooth Scroll
	document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
		anchor.addEventListener('click', function (e) {
			e.preventDefault(); // Prevent default anchor click behavior
			document.querySelector(this.getAttribute('href')).scrollIntoView({
				behavior: 'smooth',
			});
		});
	});

	// Toast Notification Function
	function showToast(message, duration = 3000) {
		const toast = document.getElementById('toast');
		toast.textContent = message;
		toast.classList.remove('hidden');
		setTimeout(() => {
			toast.classList.add('hidden');
		}, duration);
	}

	// Example of triggering toast notification on page load
	showToast('Welcome to The Cutting Edge Blog!');

	// Card Animations
	const cards = document.querySelectorAll('.card');
	cards.forEach((card) => {
		card.addEventListener('mouseover', () => {
			card.classList.add('transform', 'scale-105');
		});
		card.addEventListener('mouseout', () => {
			card.classList.remove('transform', 'scale-105');
		});
	});

	// Example Pop-Up Functionality
	document.querySelectorAll('.news-image').forEach((img) => {
		img.addEventListener('click', (e) => {
			e.preventDefault(); // Prevent default behavior on image click (if it has a link)
			alert('This is a news image!');
		});
	});

	// Prevent default form submission and show a toast instead
	const contactForm = document.querySelector(
		'form[action="{{ url_for("contact") }}"]'
	);
	if (contactForm) {
		contactForm.addEventListener('submit', (e) => {
			e.preventDefault(); // Prevent default form submission
			showToast('Form submitted successfully!');
		});
	}
});

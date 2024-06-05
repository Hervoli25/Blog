document.addEventListener('DOMContentLoaded', () => {
	// Smooth Scroll
	document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
		anchor.addEventListener('click', function (e) {
			e.preventDefault();
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
			e.preventDefault();
			alert('This is a news image!');
		});
	});

	// Prevent default form submission and show a toast instead
	const contactForm = document.querySelector('form[action="/contact"]');
	if (contactForm) {
		contactForm.addEventListener('submit', (e) => {
			e.preventDefault();
			const formData = new FormData(contactForm);
			fetch('/contact', {
				method: 'POST',
				body: formData,
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.success) {
						showToast('Form submitted successfully!');
						contactForm.reset(); // Reset the form fields
					} else {
						showToast('There was an error with your submission.');
					}
				})
				.catch((error) => {
					showToast('There was an error with your submission.');
				});
		});
	}

	// Chat functionality
	const socket = io.connect('http://' + document.domain + ':' + location.port);

	const chatForm = document.getElementById('chat-form');
	if (chatForm) {
		chatForm.addEventListener('submit', (e) => {
			e.preventDefault();
			const message = document.getElementById('chat-message').value;
			socket.send(message);
			document.getElementById('chat-message').value = '';
		});

		socket.on('message', (msg) => {
			const chatBox = document.getElementById('chat-box');
			const newMessage = document.createElement('div');
			newMessage.textContent = msg;
			chatBox.appendChild(newMessage);
			chatBox.scrollTop = chatBox.scrollHeight;
		});
	}

	// Follow and unfollow buttons
	const csrfToken = document
		.querySelector('meta[name="csrf-token"]')
		.getAttribute('content');
	document.querySelectorAll('.follow-button').forEach((button) => {
		button.addEventListener('click', function (event) {
			event.preventDefault();
			const userId = this.dataset.userId;
			const action = this.classList.contains('follow') ? 'follow' : 'unfollow';
			fetch(`/${action}/${userId}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrfToken,
				},
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.success) {
						if (action === 'follow') {
							this.textContent = 'Unfollow';
							this.classList.remove('follow');
							this.classList.add('unfollow');
						} else {
							this.textContent = 'Follow';
							this.classList.remove('unfollow');
							this.classList.add('follow');
						}
					}
				});
		});
	});
});

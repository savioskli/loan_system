document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Event click handler
    function handleEventClick(info) {
        const event = info.event;
        const modal = document.getElementById('eventDetailsModal');
        
        // Update modal content
        document.getElementById('eventDetailsTitle').textContent = event.title;
        document.getElementById('eventDetailsType').textContent = event.extendedProps.type;
        
        // Format date and time
        const startDate = new Date(event.start);
        const dateFormatter = new Intl.DateTimeFormat('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        const timeFormatter = new Intl.DateTimeFormat('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true 
        });
        
        document.getElementById('eventDetailsDate').textContent = dateFormatter.format(startDate);
        document.getElementById('eventDetailsTime').textContent = event.allDay ? 'All day' : timeFormatter.format(startDate);
        document.getElementById('eventDetailsDescription').textContent = event.extendedProps.description || 'No description provided';

        // Setup edit button
        const editBtn = document.getElementById('editEventBtn');
        editBtn.onclick = () => {
            modal.classList.add('hidden');
            openEditEventModal(event);
        };

        // Setup delete button
        const deleteBtn = document.getElementById('deleteEventBtn');
        deleteBtn.onclick = async () => {
            if (confirm('Are you sure you want to delete this event?')) {
                try {
                    const response = await fetch(`/user/api/calendar/events/${event.id}`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    });

                    if (response.ok) {
                        event.remove();
                        modal.classList.add('hidden');
                        showToast('Event deleted successfully', 'success');
                    } else {
                        const data = await response.json();
                        throw new Error(data.error || 'Failed to delete event');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showToast(error.message, 'error');
                }
            }
        };

        // Show modal
        modal.classList.remove('hidden');
    }

    // Close event details modal
    window.closeEventDetailsModal = function() {
        document.getElementById('eventDetailsModal').classList.add('hidden');
    };

    // Show toast message
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50 ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // Edit event modal functions
    window.openEditEventModal = function(event) {
        const modal = document.getElementById('editEventModal');
        const form = document.getElementById('editEventForm');
        
        // Populate form fields
        document.getElementById('editEventId').value = event.id;
        document.getElementById('editEventTitle').value = event.title;
        document.getElementById('editEventType').value = event.extendedProps.type;
        
        const startDate = new Date(event.start);
        document.getElementById('editEventDate').value = startDate.toISOString().split('T')[0];
        document.getElementById('editEventTime').value = startDate.toTimeString().slice(0, 5);
        document.getElementById('editEventDescription').value = event.extendedProps.description || '';

        // Show modal
        modal.classList.remove('hidden');

        // Handle form submission
        form.onsubmit = async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';

            try {
                const formData = {
                    title: document.getElementById('editEventTitle').value,
                    type: document.getElementById('editEventType').value,
                    date: document.getElementById('editEventDate').value,
                    time: document.getElementById('editEventTime').value,
                    description: document.getElementById('editEventDescription').value
                };

                const response = await fetch(`/user/api/calendar/events/${event.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const updatedEventData = await response.json();
                    
                    // Update the event in the calendar
                    event.setProp('title', updatedEventData.title);
                    event.setExtendedProp('type', updatedEventData.type);
                    event.setExtendedProp('description', updatedEventData.description);
                    event.setStart(new Date(updatedEventData.start));
                    if (updatedEventData.end) {
                        event.setEnd(new Date(updatedEventData.end));
                    }
                    
                    modal.classList.add('hidden');
                    showToast('Event updated successfully', 'success');
                } else {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to update event');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast(error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        };
    };

    window.closeEditEventModal = function() {
        document.getElementById('editEventModal').classList.add('hidden');
    };

    // Initialize calendar
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: false, // We're using our custom header
        height: 'auto',
        editable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        eventClassNames: function(arg) {
            return [`event-${arg.event.extendedProps.type || 'other'}`];
        },
        views: {
            dayGridMonth: {
                dayMaxEvents: 4,
                fixedWeekCount: false
            },
            timeGridWeek: {
                slotMinTime: '07:00:00',
                slotMaxTime: '19:00:00',
                expandRows: true
            },
            timeGridDay: {
                slotMinTime: '07:00:00',
                slotMaxTime: '19:00:00',
                expandRows: true
            }
        },
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short'
        },
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short'
        },
        select: function(info) {
            document.getElementById('eventDate').value = info.startStr;
            // Set default time to current time rounded to nearest half hour
            const now = new Date();
            now.setMinutes(Math.ceil(now.getMinutes() / 30) * 30);
            const timeStr = now.toTimeString().slice(0, 5);
            document.getElementById('eventTime').value = timeStr;
            openNewEventModal();
        },
        eventClick: handleEventClick,
        eventContent: function(arg) {
            const event = arg.event;
            const timeText = event.start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
            
            return {
                html: `
                    <div class="fc-event-main-frame p-1">
                        <div class="fc-event-time text-xs">${timeText}</div>
                        <div class="fc-event-title-container">
                            <div class="fc-event-title text-sm font-medium">${event.title}</div>
                        </div>
                    </div>
                `
            };
        }
    });
    calendar.render();

    // Handle calendar view controls
    document.getElementById('prevMonth').addEventListener('click', () => {
        calendar.prev();
        updateCurrentMonth();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        calendar.next();
        updateCurrentMonth();
    });

    document.getElementById('todayBtn').addEventListener('click', () => {
        calendar.today();
        updateCurrentMonth();
    });

    document.getElementById('calendarView').addEventListener('change', (e) => {
        calendar.changeView(e.target.value);
        updateCurrentMonth();
    });

    // Update current month display with a more detailed format
    function updateCurrentMonth() {
        const date = calendar.getDate();
        const view = calendar.view;
        let displayText = '';

        if (view.type === 'timeGridDay') {
            displayText = date.toLocaleDateString('default', { 
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
        } else if (view.type === 'timeGridWeek') {
            const endDate = new Date(date);
            endDate.setDate(date.getDate() + 6);
            displayText = `${date.toLocaleDateString('default', { month: 'short', day: 'numeric' })} - ${
                endDate.toLocaleDateString('default', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        } else {
            displayText = date.toLocaleDateString('default', { 
                month: 'long',
                year: 'numeric'
            });
        }
        
        document.getElementById('currentMonth').textContent = displayText;
    }
    updateCurrentMonth();

    // Modal handling with improved transitions
    const modal = document.getElementById('newEventModal');
    const newEventBtn = document.getElementById('newEventBtn');
    const closeModalBtn = document.getElementById('closeModal');
    const eventForm = document.getElementById('newEventForm');

    function openNewEventModal() {
        modal.classList.remove('hidden');
        setTimeout(() => modal.querySelector('.relative').classList.add('transform', 'translate-y-0', 'opacity-100'), 10);
    }

    function closeNewEventModal() {
        modal.querySelector('.relative').classList.remove('transform', 'translate-y-0', 'opacity-100');
        setTimeout(() => modal.classList.add('hidden'), 300);
        eventForm.reset();
    }

    newEventBtn.addEventListener('click', openNewEventModal);
    closeModalBtn.addEventListener('click', closeNewEventModal);

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeNewEventModal();
        }
    });

    // Handle form submission with improved feedback
    eventForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = eventForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';
        
        const formData = {
            title: document.getElementById('eventTitle').value,
            type: document.getElementById('eventType').value,
            date: document.getElementById('eventDate').value,
            time: document.getElementById('eventTime').value,
            description: document.getElementById('eventDescription').value,
            all_day: false
        };

        try {
            const response = await fetch('/user/api/calendar/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const eventData = await response.json();
                calendar.addEvent({
                    id: eventData.id,
                    title: eventData.title,
                    start: eventData.start,
                    end: eventData.end,
                    allDay: eventData.allDay,
                    extendedProps: {
                        type: eventData.type,
                        description: eventData.description
                    }
                });
                closeNewEventModal();
                
                // Show success message
                const toast = document.createElement('div');
                toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
                toast.textContent = 'Event created successfully';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save event');
            }
        } catch (error) {
            console.error('Error:', error);
            // Show error message
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
            toast.textContent = error.message || 'Failed to create event';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });

    // Initial load of events with loading state
    async function loadEvents() {
        calendarEl.classList.add('opacity-50');
        try {
            const response = await fetch('/user/api/calendar/events', {
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';  // Redirect to login if unauthorized
                    return;
                }
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const events = await response.json();
            events.forEach(eventData => {
                calendar.addEvent({
                    id: eventData.id,
                    title: eventData.title,
                    start: eventData.start,
                    end: eventData.end,
                    allDay: eventData.allDay,
                    extendedProps: {
                        type: eventData.type,
                        description: eventData.description
                    }
                });
            });
        } catch (error) {
            console.error('Error loading events:', error);
            // Show error message
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50';
            toast.textContent = error.message || 'Failed to load events';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        } finally {
            calendarEl.classList.remove('opacity-50');
        }
    }

    loadEvents();
});

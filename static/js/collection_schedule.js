document.addEventListener('DOMContentLoaded', function() {
    // Load collection schedules for a staff
    function loadCollectionSchedules() {
        $.ajax({
            url: '/collection_schedule',
            method: 'GET',
            success: function(schedules) {
                const scheduleList = $('#collectionSchedulesList');
                scheduleList.empty();
                schedules.forEach(schedule => {
                    scheduleList.append(`
                        <div class="p-4 bg-gray-100 rounded-lg shadow-sm">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="text-lg font-semibold">Schedule ID: ${schedule.id}</h3>
                                    <p>Loan ID: ${schedule.loan_id}</p>
                                    <p>Staff ID: ${schedule.staff_id}</p>
                                    <p>Date: ${new Date(schedule.schedule_date).toLocaleString()}</p>
                                    <p>Status: ${schedule.status}</p>
                                </div>
                                <div class="flex space-x-2">
                                    <button class="edit-schedule-btn bg-blue-500 text-white px-3 py-1 rounded" data-id="${schedule.id}">Edit</button>
                                    <button class="delete-schedule-btn bg-red-500 text-white px-3 py-1 rounded" data-id="${schedule.id}">Delete</button>
                                </div>
                            </div>
                        </div>
                    `);
                });
            }
        });
    }

    // Create a new collection schedule
    $('#newCollectionScheduleForm').submit(function(event) {
        event.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            url: '/collection_schedule',
            method: 'POST',
            data: formData,
            success: function(response) {
                alert(response.message);
                $('#newCollectionScheduleModal').hide();
                loadCollectionSchedules();
            }
        });
    });

    // Delete a collection schedule
    $(document).on('click', '.delete-schedule-btn', function() {
        const scheduleId = $(this).data('id');
        $.ajax({
            url: `/collection_schedule/${scheduleId}`,
            method: 'DELETE',
            success: function(response) {
                alert(response.message);
                loadCollectionSchedules();
            }
        });
    });

    // Initialize collection schedules on page load
    loadCollectionSchedules();
});

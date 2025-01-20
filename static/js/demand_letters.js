document.addEventListener('DOMContentLoaded', function() {
    // Initialize member select
    $(document).ready(function() {
        initializeMemberSelect('#member_id');
    });

    function initializeMemberSelect(selector) {
        console.log('Initializing select2 for:', selector);
        const select = $(selector);

        const config = {
            theme: 'bootstrap-5',
            placeholder: 'Search for a member...',
            allowClear: true,
            width: '100%',
            ajax: {
                url: '/api/customers/search',  
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    console.log('Search params:', params);
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function(data, params) {
                    console.log('Received data:', data);
                    params.page = params.page || 1;
                    return {
                        results: data.items.map(item => ({
                            id: item.id,
                            text: item.text,
                            member_no: item.id,
                            phone: item.loans && item.loans.length > 0 ? item.loans[0].phone : '',
                            email: item.loans && item.loans.length > 0 ? item.loans[0].email : ''
                        })),
                        pagination: {
                            more: data.has_more
                        }
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            templateResult: formatMember,
            templateSelection: formatMemberSelection
        };

        select.select2(config);
    }

    function formatMember(member) {
        if (!member.id) {
            return member.text;
        }
        return $(`
            <div class="select2-member-result">
                <div class="member-name">${member.text}</div>
                <small class="member-details">
                    ${member.member_no ? 'Member No: ' + member.member_no : ''}
                    ${member.phone ? '| Phone: ' + member.phone : ''}
                    ${member.email ? '| Email: ' + member.email : ''}
                </small>
            </div>
        `);
    }

    function formatMemberSelection(member) {
        return member.text;
    }

    // Load template content when a template is selected
    $('#letter_template_id').on('change', function() {
        const selectedTemplateId = $(this).val();
        if (!selectedTemplateId) return;

        $.ajax({
            url: `/routes/get_letter_template/${selectedTemplateId}`,
            method: 'GET',
            success: function(response) {
                $('#letter_content').val(response.template_content);
            },
            error: function() {
                console.error('Failed to load letter template');
                alert('Failed to load letter template');
            }
        });
    });
});

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

    // Dynamically populate letter templates based on letter type
    $('#letter_type_id').on('change', function() {
        var letterTypeId = $(this).val();
        $.ajax({
            url: '/api/letter_templates',
            method: 'GET',
            data: { letter_type_id: letterTypeId },
            success: function(response) {
                var $templateSelect = $('#letter_template_id');
                $templateSelect.empty();
                
                // Check if response has templates
                if (response && response.length > 0) {
                    response.forEach(function(template) {
                        $templateSelect.append(
                            $('<option>', {
                                value: template.id,
                                text: template.name,
                                'data-content': template.template_content
                            })
                        );
                    });
                } else {
                    $templateSelect.append(
                        $('<option>', {
                            value: '',
                            text: 'No templates available'
                        })
                    );
                }
                $templateSelect.trigger('change');
            },
            error: function() {
                var $templateSelect = $('#letter_template_id');
                $templateSelect.empty();
                $templateSelect.append(
                    $('<option>', {
                        value: '',
                        text: 'Error loading templates'
                    })
                );
                $templateSelect.trigger('change');
            }
        });
    });

    // Load template content when a template is selected
    $('#letter_template_id').on('change', function() {
        var $selectedOption = $(this).find('option:selected');
        var templateContent = $selectedOption.data('content') || '';
        $('#letter_content').val(templateContent);
    });
});

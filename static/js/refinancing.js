document.addEventListener('DOMContentLoaded', function() {
    $(document).ready(function() {
        // CSRF Token Setup
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });

        // Global variables to store selections
        let currentMemberData = null;
        let currentEditMemberData = null;

        function initializeMemberSelect() {
            if ($('#member_id').hasClass("select2-hidden-accessible")) {
                $('#member_id').select2('destroy');
            }

            $('#member_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Search for a client...',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#add-modal'),
                containerCssClass: "select2-container--custom",
                dropdownCssClass: "select2-dropdown--custom",
                ajax: {
                    url: '/api/customers/search',
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            q: params.term || '',
                            page: params.page || 1
                        };
                    },
                    processResults: function(data) {
                        if (!data || !data.items || !Array.isArray(data.items)) {
                            console.error('Invalid data structure', data);
                            return { results: [] };
                        }

                        const results = data.items.map(item => ({
                            id: item.id || '',
                            text: item.text || 'Unknown Client',
                            loans: Array.isArray(item.loans) ? item.loans : [],
                            _originalItem: item
                        }));

                        return {
                            results: results,
                            pagination: {
                                more: data.has_more || false
                            }
                        };
                    },
                    cache: true
                },
                minimumInputLength: 2,
                templateResult: function(item) {
                    if (!item.id) return item.text;

                    const loans = item.loans || [];
                    const loanInfo = loans.length > 0
                        ? `${loans.length} loan(s), Total Outstanding: ${formatCurrency(
                            loans.reduce((total, loan) => total + (loan.OutstandingBalance || 0), 0)
                        )}`
                        : 'No loans';

                    return $(`
                        <div>
                            <strong>${item.text}</strong>
                            <br>
                            <small>${loanInfo}</small>
                        </div>
                    `);
                }
            }).on('select2:select', function(e) {
                currentMemberData = e.params.data;

                const loanSelect = $('#loan_id');
                loanSelect.empty().append(new Option('Select a loan', '', true, true));

                if (currentMemberData &&
                    currentMemberData.loans &&
                    Array.isArray(currentMemberData.loans) &&
                    currentMemberData.loans.length > 0) {

                    currentMemberData.loans.forEach(loan => {
                        const loanNo = loan.LoanNo || 'Unknown Loan';
                        const outstandingBalance = loan.OutstandingBalance || 0;
                        const loanAppId = loan.LoanAppID || '';

                        const option = new Option(
                            `${loanNo} (Outstanding: ${formatCurrency(outstandingBalance)})`,
                            loanAppId,
                            false,
                            false
                        );
                        $(option).data('loan', loan);
                        loanSelect.append(option);
                    });
                } else {
                    loanSelect.append(new Option('No loans available', '', true, true));
                }

                loanSelect.trigger('change');

                // Set the member name in the hidden input field
                $('#member_name').val(currentMemberData.text);
            }).on('select2:clear', function() {
                currentMemberData = null;
                $('#loan_id').empty().append(new Option('Select a loan', '', true, true)).trigger('change');
                $('#member_name').val('');
            });
        }

        function initializeEditMemberSelect() {
            if ($('#edit_member_id').hasClass("select2-hidden-accessible")) {
                $('#edit_member_id').select2('destroy');
            }

            $('#edit_member_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Search for a client...',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#edit-modal'),
                containerCssClass: "select2-container--custom",
                dropdownCssClass: "select2-dropdown--custom",
                ajax: {
                    url: '/api/customers/search',
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            q: params.term || '',
                            page: params.page || 1
                        };
                    },
                    processResults: function(data) {
                        if (!data || !data.items || !Array.isArray(data.items)) {
                            console.error('Invalid data structure', data);
                            return { results: [] };
                        }

                        const results = data.items.map(item => ({
                            id: item.id || '',
                            text: item.text || 'Unknown Client',
                            loans: Array.isArray(item.loans) ? item.loans : [],
                            _originalItem: item
                        }));

                        return {
                            results: results,
                            pagination: {
                                more: data.has_more || false
                            }
                        };
                    },
                    cache: true
                },
                minimumInputLength: 2,
                templateResult: function(item) {
                    if (!item.id) return item.text;

                    const loans = item.loans || [];
                    const loanInfo = loans.length > 0
                        ? `${loans.length} loan(s), Total Outstanding: ${formatCurrency(
                            loans.reduce((total, loan) => total + (loan.OutstandingBalance || 0), 0)
                        )}`
                        : 'No loans';

                    return $(`
                        <div>
                            <strong>${item.text}</strong>
                            <br>
                            <small>${loanInfo}</small>
                        </div>
                    `);
                }
            }).on('select2:select', function(e) {
                currentEditMemberData = e.params.data;

                const loanSelect = $('#edit_loan_id');
                loanSelect.empty().append(new Option('Select a loan', '', true, true));

                if (currentEditMemberData &&
                    currentEditMemberData.loans &&
                    Array.isArray(currentEditMemberData.loans) &&
                    currentEditMemberData.loans.length > 0) {

                    currentEditMemberData.loans.forEach(loan => {
                        const loanNo = loan.LoanNo || 'Unknown Loan';
                        const outstandingBalance = loan.OutstandingBalance || 0;
                        const loanAppId = loan.LoanAppID || '';

                        const option = new Option(
                            `${loanNo} (Outstanding: ${formatCurrency(outstandingBalance)})`,
                            loanAppId,
                            false,
                            false
                        );
                        $(option).data('loan', loan);
                        loanSelect.append(option);
                    });
                } else {
                    loanSelect.append(new Option('No loans available', '', true, true));
                }

                loanSelect.trigger('change');

                // Set the member name in the hidden input field
                $('#edit_member_name').val(currentEditMemberData.text);
            }).on('select2:clear', function() {
                currentEditMemberData = null;
                $('#edit_loan_id').empty().append(new Option('Select a loan', '', true, true)).trigger('change');
                $('#edit_member_name').val('');
            });
        }

        function initializeLoanSelect() {
            $('#loan_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Select a Loan',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#add-modal'),
                containerCssClass: "select2-container--custom",
                dropdownCssClass: "select2-dropdown--custom"
            }).on('select2:select', function(e) {
                const selectedLoanId = e.target.value;
                const loan = $(e.target.selectedOptions[0]).data('loan');

                if (loan && loan.OutstandingBalance) {
                    $('#current_balance').val(loan.OutstandingBalance);
                }
            });
        }

        function initializeEditLoanSelect() {
            $('#edit_loan_id').select2({
                theme: 'bootstrap-5',
                placeholder: 'Select a Loan',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#edit-modal'),
                containerCssClass: "select2-container--custom",
                dropdownCssClass: "select2-dropdown--custom"
            }).on('select2:select', function(e) {
                const selectedLoanId = e.target.value;
                const loan = $(e.target.selectedOptions[0]).data('loan');

                if (loan && loan.OutstandingBalance) {
                    $('#edit_current_balance').val(loan.OutstandingBalance);
                }
            });
        }

        function formatCurrency(amount) {
            const safeAmount = (amount === null || amount === undefined) ? 0 : amount;

            try {
                return new Intl.NumberFormat('en-KE', {
                    style: 'currency',
                    currency: 'KES',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(safeAmount);
            } catch (error) {
                console.error('Error formatting currency:', error);
                return 'KES 0.00';
            }
        }

        // Add custom styles for Select2
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .select2-container--custom .select2-selection {
                    padding: 0.5rem 0.75rem;
                    border: 1px solid rgb(209, 213, 219);
                    border-radius: 0.5rem;
                    min-height: 42px;
                }
                .dark .select2-container--custom .select2-selection {
                    border-color: rgb(75, 85, 99);
                    background-color: rgb(55, 65, 81);
                    color: white;
                }
                .select2-container--custom .select2-selection:focus {
                    ring: 2;
                    ring-color: rgb(var(--primary-rgb));
                    border-color: rgb(var(--primary-rgb));
                }
                .select2-container--custom .select2-selection--single .select2-selection__rendered {
                    line-height: 1.5;
                    padding-left: 0;
                    padding-right: 20px;
                }
                .select2-container--custom .select2-selection--single .select2-selection__arrow {
                    height: 42px;
                }
                .select2-dropdown--custom {
                    border-color: rgb(209, 213, 219);
                    border-radius: 0.5rem;
                }
                .dark .select2-dropdown--custom {
                    border-color: rgb(75, 85, 99);
                    background-color: rgb(55, 65, 81);
                    color: white;
                }
            `)
            .appendTo('head');

        // Initialize selects
        initializeMemberSelect();
        initializeLoanSelect();
        initializeEditMemberSelect();
        initializeEditLoanSelect();
    });
});
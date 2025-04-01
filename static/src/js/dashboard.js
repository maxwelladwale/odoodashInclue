// static/src/js/dashboard.js
odoo.define('facilitation_dashboard.Dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    var FacilitationDashboard = AbstractAction.extend({
        template: 'facilitation_dashboard.Dashboard',
        events: {
            'click .o_refresh_dashboard': '_onRefreshDashboard',
        },

        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.dashboardData = {};
        },

        willStart: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                return self._fetchDashboardData();
            });
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._renderDashboard();
            });
        },

        _fetchDashboardData: function() {
            var self = this;
            return rpc.query({
                route: '/facilitation_dashboard/data',
                params: {},
            }).then(function(result) {
                self.dashboardData = result;
            });
        },

        _renderDashboard: function() {
            var self = this;
            
            // Render summary tiles
            var $summary = $(QWeb.render('facilitation_dashboard.Summary', {
                summary: this.dashboardData.summary,
            }));
            this.$('.o_dashboard_summary').empty().append($summary);
            
            // Render charts
            this._renderSessionsChart();
            this._renderResponseRatesChart();
        },

        _renderSessionsChart: function() {
            var ctx = this.$('#sessions_chart')[0].getContext('2d');
            var data = this.dashboardData.sessions_by_month;
            
            var labels = [];
            var counts = [];
            
            _.each(data, function(item) {
                labels.push(item.month);
                counts.push(item.count);
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Sessions',
                        data: counts,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },

        _renderResponseRatesChart: function() {
            var ctx = this.$('#response_rates_chart')[0].getContext('2d');
            var data = this.dashboardData.response_rates;
            
            var labels = [];
            var responseRates = [];
            var followupRates = [];
            
            _.each(data, function(item) {
                labels.push(item.session_name);
                responseRates.push(item.total_participants ? (item.responded / item.total_participants) * 100 : 0);
                followupRates.push(item.total_participants ? (item.followed_up / item.total_participants) * 100 : 0);
            });
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Response Rate',
                        data: responseRates,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }, {
                        label: 'Follow-up Rate',
                        data: followupRates,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        },

        _onRefreshDashboard: function() {
            var self = this;
            this._fetchDashboardData().then(function() {
                self._renderDashboard();
            });
        }
    });

    core.action_registry.add('facilitation_dashboard.dashboard', FacilitationDashboard);

    return FacilitationDashboard;
});
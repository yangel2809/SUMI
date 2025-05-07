(function($) {

	"use strict";

	$('#datetime_container').datetimepicker({
    allowInputToggle: true,
    showClear: true,
	dayViewHeaderFormat: 'MMMM YYYY',
	format: 'DD/MM/YYYY H:mm:ss',
	locale: 'es',
	useCurrent: false,
	
    icons: {
		time:'fa fa-clock-o',
		date:'fa fa-calendar-o',
		up:'fa fa-chevron-up',
		down:'fa fa-chevron-down',
		previous:'fa fa-chevron-left',
		next:'fa fa-chevron-right',
		today:'fa fa-chevron-up',
		clear:'fa fa-trash',
		close:'fa fa-close'
	},
	tooltips: {
		today: 'Ir a Hoy',
		clear: 'Limpiar Selección',
		close: 'Cerrar',
		selectTime: 'Seleccionar Hora',
		selectMonth: 'Seleccionar Mes',
		selectDecade: 'Seleccionar Década',
		prevMonth: 'Mes Previo',
		nextMonth: 'Siguiente Mes',
		selectYear: 'Seleccionar Año',
		prevYear: 'Año Previo',
		nextYear: 'Año Siguiente',
		prevDecade: 'Década Previo',
		nextDecade: 'Década Siguiente',
		prevCentury: 'Siglo Previo',
		nextCentury: 'Siglo Siguiente'
	},
	});

})(jQuery);

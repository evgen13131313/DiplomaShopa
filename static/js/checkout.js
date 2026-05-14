document.addEventListener('DOMContentLoaded', function() {
    const totalElement = document.getElementById('display-total');
    const discountElement = document.getElementById('display-discount');
    const finalElement = document.getElementById('display-final');
    const discountRow = document.getElementById('discount-row');
    const radioButtons = document.querySelectorAll('input[name="payment_method"]');
    
    // Получаем базовую сумму из data-атрибута или из текста элемента
    let baseTotal = 0;
    if (totalElement && totalElement.dataset.value) {
        baseTotal = parseFloat(totalElement.dataset.value);
    } else {
        // Если data-value нет, берём из текста и парсим
        const totalText = totalElement ? totalElement.textContent : '0';
        baseTotal = parseFloat(totalText.toString().replace(/\s/g, '').replace(',', '.'));
    }
    
    const discountRate = 0.10; // 10%
    
    function updatePrice() {
        const selected = document.querySelector('input[name="payment_method"]:checked');
        let discount = 0;
        let final = baseTotal;
        
        if (selected && selected.value === 'wallet') {
            discount = baseTotal * discountRate;
            final = baseTotal - discount;
            // Показываем строку со скидкой
            if (discountRow) discountRow.style.display = 'flex';
        } else {
            // Скрываем строку со скидкой
            if (discountRow) discountRow.style.display = 'none';
        }
        
        // Обновляем текст с форматированием (пробелы между тысячами)
        if (totalElement) {
            totalElement.textContent = baseTotal.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
        if (discountElement) {
            discountElement.textContent = '-' + discount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
        if (finalElement) {
            finalElement.textContent = final.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
    }
    
    // Вешаем событие на все радио-кнопки оплаты
    radioButtons.forEach(radio => {
        radio.addEventListener('change', updatePrice);
    });
    
    // Запускаем при загрузке
    updatePrice();
});
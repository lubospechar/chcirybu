{% comment %} /* Tohle celé zařídí přidávání z řádek do formfactory */ {% endcomment %}
$( document ).ready(function() {
    
    {% comment %} /* Vezmi formulář vytvořený z formfactory.empty_form a ulož ho jako vzor */ {% endcomment %}
    const empty_form = $('#empty-order-fish-form > ul') 
        
    $('#add-button').click(function( eventObject ) {
        eventObject.preventDefault();
        
        {% comment %} /* najdi div ve kterém jsou řádky formuláře a zjisti kolik jich tam je */ {% endcomment %}
        var order_fish_form = $('#order-fish-form');
        var fish_rows = order_fish_form.children('ul').length;
        
        {% comment %} /* udělej kopii vzorového prázdného formuláře */ {% endcomment %}  
        var new_form = empty_form.clone();
        
        {% comment %} /* přepiš přepiš veškeré defaultní atributy na adributy určující pořadí řádku (zaměnit __prefix__ za číslo určující pořadí */ {% endcomment %}
        new_form.find('[id^=id_form-__prefix__]').each(function() { 
            var default_id = $(this).attr('id')
            var new_id = default_id.replace('__prefix__', fish_rows)
            var new_name = new_id.replace('id_', '')
                
            $(this).attr('id', new_id)
            $(this).attr('name', new_name)
            $(this).prev().attr('for', new_id)
        });
        
        {% comment %} /* napiš kolik má formulář reálných řádek */ {% endcomment %}
        $('#id_form-TOTAL_FORMS').attr('value', fish_rows + 1);

        order_fish_form.append(new_form);
        
    });
}); 

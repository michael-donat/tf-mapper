# Co mapper wysyla 

room:enter
--------------
   -    ustawia default state (resetuje wszystko co poprzedni pokoj ustawil) (wywala np skrypty pokoju)
   -    zeruje podmiane kierunkow na numeryku (``/quote -S /unset `/listvar _map_custom_exit_rebind_*``)
   -    resetuje wyswietlanie custom exists w statusbarze (jak ktos ma)
   -    zeruje ustawienia wyjsc (_map_custom_exits_counter i _map_custom_exits_count)

room:id
--------------
   -    ustawia zmienna room id

exit:start
--------------

exit:custom:(.*)
--------------
   -     ustawia customowe wyjscie

exit:rebind:([A-Z]{1,2}):(.*)
--------------
   -     ustawia customowe wyjscie na kierunek (``/eval /set %%_map_custom_exit_rebind_%{P1} = %{P2}``)

exit:end
--------------
   -     kompiluje customowe wyjscia
   -     wywoluje funkcje _map_custom_exit_switch
   -     wywoluje funkcje (_map_custom_exit_show) (funkja nie powinna znajdowac sie w map.tf)
   
# Co mapper odbiera

navigate:exit:(.*)
---------
   - kulka ruszy sie w wyslanym kierunku jesli pokoj istnieje

navigate:custom:(.*)
---------
   - kulka ruszy w kierunku ktory ma zdefiniowany rebind jaki zostal wyslany (np. wyjscie)

navigate:follow:(.*)
-------
   - kulka ruszy w kierunku ktory ma zdefiniowany follow jaki zostaj wyslany (np. do wyjscia)

revert
------
   - kulka wroci do poprzedniego pokoju

lookup:(.*)
----
   - kulka ustawi pokoj o wyslanym id

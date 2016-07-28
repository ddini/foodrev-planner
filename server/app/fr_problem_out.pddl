

        (define (problem foodrev-1)
            (:domain
                foodrev-domain
            )

            (:objects
                loc1 loc2 loc3
                Alice Bob Charlie
                car1 car2
            )

            (:init
                (person Alice)
(person Bob)
(person Charlie)

                (location loc1)
(location loc2)
(location loc3)

                (car car1)
(car car2)


                (at Alice loc1)
(at Bob loc1)
(at Charlie loc1)

                (at car1 loc1)
(at car2 loc2)


                (= (supply loc2) 200)

                (= (demand loc3) 200)


                (= (car-capacity car1) 100)
(= (car-capacity car2) 100)


                (= (trips-taken Alice) 0)
(= (trips-taken Bob) 0)
(= (trips-taken Charlie) 0)


                (= (number-trips) 0)
            )

            (:goal
                (<= (demand location1) 0)
            )

            (:metric minimize (number-trips))
        )

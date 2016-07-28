(define (domain foodrev-domain)
	(:functions
		(number-trips)
		(supply ?location)
		(demand ?location)

		(trips-taken ?person)
		(car-capacity ?car)
	)

	(:predicates
		(carrying-load ?car)
		(at ?person ?location)
		(location ?location)
		(car ?car)
		(assigned ?person ?car)
		(person ?person)
		(is-assigned ?person)		
	)

	(:action drive
		:parameters (?person ?car ?from-loc ?to-loc)
		:precondition (and
					(person ?person)
					(at ?car ?from-loc)
					(assigned ?person ?car)
				)
		:effect (and
				(at ?car ?to-loc)
				(not (at ?car ?from-loc))
				(increase (number-trips) 1)
				(increase (trips-taken ?person) 1)
			)
	
	)

	(:action load
		:parameters (?car ?location)
		:precondition (and
					(> (supply ?location) 0)
					(at ?car ?location)
					(location ?location)
					(car ?car)
					(not (carrying-load ?car))
				)

		:effect (and
				(decrease (supply ?location) (car-capacity ?car))
				(carrying-load ?car)
			)
	)

	(:action unload
		:parameters (?car ?location)
		:precondition (and
					(> (demand ?location) 0)
					(carrying-load ?car)
					(location ?location)
					(car ?car)
					(at ?car ?location)
				)
		:effect (and
				(decrease (demand ?location) (car-capacity ?car))		
				(not (carrying-load ?car))
			)
	)

	(:action assign-car
		:parameters (?person ?car ?location)
		:precondition (and
					(person ?person)
					(car ?car)
					(not (is-assigned ?person))
					(at ?car ?location)
					(at ?person ?location)
				)
		:effect (and
				(assigned ?person ?car)
				(is-assigned ?person)
				(not (at ?person ?location))
			)
	)

)

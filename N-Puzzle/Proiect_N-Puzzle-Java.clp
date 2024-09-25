
(deffunction take-board (?input)
    (bind ?elem (read ?input))
    (bind ?board (create$ ?elem))

    (while (neq ?elem EOF)
        (bind ?elem (read ?input))
        (if (and (neq ?elem " ") (neq ?elem EOF))
            then (bind ?board (insert$ ?board (+ 1 (length$ ?board)) ?elem))))
    (return ?board))


(deffunction create-list (?size)
  (bind ?list (create$))

  (loop-for-count (?i 1 ?size)
    (bind ?list (insert$ ?list  ?i 0)))
  (return ?list))


(deffunction is-final-state (?state)
    (bind ?size (length$ ?state))
    (bind ?final-state (create$))

    (loop-for-count (?i 1 ?size)
        (bind ?final-state (insert$ ?final-state ?i ?i)))
    
    (if (eq (nth$ ?size ?final-state) ?size)
        then (bind ?final-state (replace$ ?final-state ?size ?size 0)))

        (if (neq ?final-state ?state)
            then (return FALSE))

    (return TRUE))


(deffunction final-state (?size)
    (bind ?final (create$))
    (loop-for-count (?i 1 ?size)
        (bind ?final (insert$ ?final ?i ?i)))
    
    (if (eq (nth$ ?size ?final) ?size)
        then (bind ?final (replace$ ?final ?size ?size 0)))
    
    (return ?final))


(deffunction validate-board (?board)
    (bind ?size (length$ ?board))
    (bind ?used (create-list ?size))
    (bind ?size-used (length$ ?used))

    (if (< ?size 2)
        then (printout output "Tabla este prea mica!" crlf)
             (return FALSE))

    (loop-for-count (?i 1 ?size)
        (bind ?num (nth$ ?i ?board))
        (if (or (< ?num 0) (> ?num ?size))
            then (printout output "Exista un numar invalid!" crlf)
                 (return FALSE))
        (if (eq ?num 0)
            then (bind ?num ?size-used)
                 (bind ?used (replace$ ?used ?num ?num 1)))
        (if (and (eq (nth$ ?num ?used) 1) (< ?num ?size-used))
                      then (printout output "Exista un numar care se repeta!" crlf)
                           (return FALSE)
                      else (bind ?used (replace$ ?used ?num ?num 1))))

    (bind ?ok FALSE)
    (loop-for-count (?i 1 ?size)
        (if (or (eq (nth$ ?i ?used) 0) (> (nth$ ?i ?used) 1))
            then (return FALSE))
        (if (eq (nth$ ?i ?board) 0)
            then (bind ?ok TRUE)))

    (return ?ok))


(deffunction check-board (?board)
    (if (validate-board ?board) then
        (printout output "Tabla este valida." crlf)
        (return TRUE)
    else
        (printout output "Tabla nu este valida." crlf)
        (return FALSE)))


(deffunction count-inversions (?board)
    (bind ?inversions 0)
    (bind ?size (length$ ?board))

    (loop-for-count (?i 1 ?size)
        (bind ?current (nth$ ?i ?board))
        (if (neq ?current 0)
            then
                (loop-for-count (?j (+ ?i 1) ?size)
                    (bind ?next (nth$ ?j ?board))
                    (if (and (neq ?next 0) (< ?next ?current))
                        then
                            (bind ?inversions (+ ?inversions 1))))))
    (return ?inversions))


(deffunction find-zero-position (?board)
    (bind ?size (length$ ?board))

    (loop-for-count (?i 1 ?size)
        (if (eq (nth$ ?i ?board) 0)
            then (return ?i)))
    (return -1))


(deffunction is-solvable (?board)
    (if (is-final-state ?board)
        then (return TRUE))

    (bind ?size-board (length$ ?board))
    (bind ?size (integer (sqrt ?size-board)))
    (bind ?inversions (count-inversions ?board))
    (bind ?zero-pos (find-zero-position ?board))
    (bind ?zero-row (integer (+ 1 (/ (- ?zero-pos 1) ?size))))

    (if (eq (mod ?size 2) 1)
        then (return (eq (mod ?inversions 2) 0)))

    (if (and (eq (mod ?zero-row 2) 1) (eq (mod ?inversions 2) 1))
                then (return TRUE))

    (if (and (eq (mod ?zero-row 2) 0) (eq (mod ?inversions 2) 0))
                then (return TRUE))
    
    (return FALSE))


(deffunction swap-positions (?state ?pos1 ?pos2)
    (bind ?value1 (nth$ ?pos1 ?state))
    (bind ?value2 (nth$ ?pos2 ?state))
    (bind ?new-state (replace$ ?state ?pos1 ?pos1 ?value2))
    (bind ?new-state (replace$ ?new-state ?pos2 ?pos2 ?value1))

    (return ?new-state))


(deffunction enqueue (?queue ?state)
    (return (create$ ?queue ?state)))


(deffunction dequeue (?queue ?size)
    (if (> (length$ ?queue) ?size)
        then (return (subseq$ ?queue (+ ?size 1) (length$ ?queue)))
        else (return (create$))))


(deffunction dedequeue (?queue ?size)
    (if (> (length$ ?queue) ?size)
        then (return (subseq$ ?queue 0 (- (length$ ?queue) ?size)))
        else (return (create$))))


(deffunction front (?queue ?size)
    (bind ?state (create$))

    (loop-for-count (?i 1 ?size)
        (bind ?state (insert$ ?state ?i (nth$ ?i ?queue))))
    (return ?state))

(deffunction back (?queue ?size)
    (bind ?state (create$))
    (bind ?i 1)

    (while (> ?size 0)
        (bind ?state (insert$ ?state ?i (nth$ (- (+ (length$ ?queue) 1) ?size) ?queue)))
        (bind ?i (+ ?i 1))
        (bind ?size (- ?size 1)))
    (return ?state))


(deffunction state-equal (?state1 ?state2)
    (return (eq ?state1 ?state2)))


(deffunction remove-que (?queue ?item)
    (bind ?new-que (create$))
    (bind ?queue-size (length$ ?queue))
    (bind ?item-size (length$ ?item))
    (bind ?count-size (integer (/ ?queue-size ?item-size)))

    (loop-for-count (?i 1 ?count-size)
        (bind ?question (front ?queue ?item-size))
        (bind ?queue (dequeue ?queue ?item-size))
        (if (not (state-equal ?item ?question))
            then (bind ?new-que (enqueue ?new-que ?question))))

    (return ?new-que))


(deffunction find-back-move (?state ?move)
    (bind ?size-board (length$ ?state))
    (bind ?size (integer (sqrt ?size-board)))
    (bind ?new-state (create$))
    (bind ?new-move (create$))
    (bind ?zero-pos (find-zero-position ?state))

    (if (eq ?move up)
        then (bind ?new-move down)
             (bind ?new-state (swap-positions ?state ?zero-pos (+ ?size ?zero-pos))))

    (if (eq ?move down)
        then (bind ?new-move up)
             (bind ?new-state (swap-positions ?state ?zero-pos (- ?zero-pos ?size))))

    (if (eq ?move right)
        then (bind ?new-move left)
             (bind ?new-state (swap-positions ?state ?zero-pos (- ?zero-pos 1))))

    (if (eq ?move left)
        then (bind ?new-move right)
             (bind ?new-state (swap-positions ?state ?zero-pos (+ 1 ?zero-pos))))
             
    (bind ?result (create$ ?new-state ?new-move))
    (return ?result))


(deffunction inbound (?new-x ?new-y ?size)
    (if (and (>= ?new-x 0) (< ?new-x ?size) (>= ?new-y 0) (< ?new-y ?size))
        then (return TRUE))
    (return FALSE))


(deffunction diag (?new-x ?new-y ?state ?size)
    (bind ?zero (find-zero-position ?state))
    (bind ?zero-x (mod (- ?zero 1) ?size))
    (bind ?zero-y (integer (/ (- ?zero 1) ?size)))

    (if (and (eq ?new-x ?zero-x) (or (eq ?new-y (- ?zero-y 1)) (eq ?new-y (+ ?zero-y 1))))
        then (return TRUE))
    (if (and (eq ?new-y ?zero-y) (or (eq ?new-x (- ?zero-x 1)) (eq ?new-x (+ ?zero-x 1))))
        then (return TRUE))

    (return FALSE))


(deffunction insidee (?coord ?size)
    (return (and (>= ?coord 0) (< ?coord ?size))))


(deffunction neighbors-check (?pos-x ?pos-y ?state)
    (bind ?size (length$ ?state))
    (bind ?dimension (integer ( sqrt ?size)))

    (bind ?x1 (- ?pos-x 1))
    (bind ?x2 (+ ?pos-x 1))
    (bind ?y1 (- ?pos-y 1))
    (bind ?y2 (+ ?pos-y 1))

    (if (and (insidee ?x1 ?dimension) (> (nth$ (+ 1 (* ?pos-y ?dimension) ?x1) ?state) (nth$ (+ 1 (* ?pos-y ?dimension) ?pos-x) ?state)))
        then (return TRUE))
    (if (and (insidee ?x2 ?dimension) (> (nth$ (+ 1 (* ?pos-y ?dimension) ?x2) ?state) (nth$ (+ 1 (* ?pos-y ?dimension) ?pos-x) ?state)))
        then (return TRUE))
    (if (and (insidee ?y1 ?dimension) (> (nth$ (+ 1 (* ?y1 ?dimension) ?pos-x) ?state) (nth$ (+ 1 (* ?pos-y ?dimension) ?pos-x) ?state)))
        then (return TRUE))
    (if (and (insidee ?y2 ?dimension) (> (nth$ (+ 1 (* ?y2 ?dimension) ?pos-x) ?state) (nth$ (+ 1 (* ?pos-y ?dimension) ?pos-x) ?state)))
        then (return TRUE))
    
    (return FALSE))


(deffunction new-rule (?new-x ?new-y ?state)
    (bind ?size (length$ ?state))
    (bind ?dimension (integer (sqrt ?size)))

    (if (eq (nth$ (+ 1 (* ?new-y ?dimension) ?new-x) ?state) (- ?size 1))
        then (return TRUE))
    
    (return (neighbors-check ?new-x ?new-y ?state)))


(deffunction ruless (?new-x ?new-y ?state)
    (bind ?size (integer (sqrt (length$ ?state))))

    (if (inbound ?new-x ?new-y ?size)
        then (return TRUE))
    (return FALSE))


(deffunction already-visited (?state ?visited)
    (if (eq (length$ ?state) 0)
        then ;(printout output "state este null" crlf)
             (return TRUE))

    (bind ?visited-size (length$ ?visited))
    (bind ?state-size (length$ ?state))
    (bind ?count-size (integer(/ ?visited-size ?state-size)))

    (loop-for-count (?i 1 ?count-size)
        (if (state-equal ?state (front ?visited ?state-size))
            then (return TRUE)
            else (bind ?visited (dequeue ?visited ?state-size))))
    (return FALSE))


(deffunction find-contor (?state ?visited)
    (bind ?visited-size (length$ ?visited))
    (bind ?state-size (length$ ?state))
    (bind ?count-size (integer(/ ?visited-size ?state-size)))

    (loop-for-count (?i 1 ?count-size)
            (if (state-equal (front ?visited ?state-size) ?state)
                then (return ?i))
            (bind ?visited (dequeue ?visited ?state-size)))
    (return -1))


(deffunction generate-neighbors (?state ?visited)
    (bind ?size (integer (sqrt (length$ ?state))))
    (bind ?neighbors (create$))
    (bind ?zero-pos (find-zero-position ?state))
    (bind ?zero-x (mod (- ?zero-pos 1) ?size))
    (bind ?zero-y (integer (/ (- ?zero-pos 1) ?size)))

    (bind ?directions (create$ (create$ -1 0 left) (create$ 1 0 right) (create$ 0 -1 up) (create$ 0 1 down)))
    (bind ?dim (integer (/ (length$ ?directions) 2)))
    (while (> (length$ ?directions) 0)
        (bind ?dir (front ?directions 3))
        (bind ?directions (dequeue ?directions 3))
        (bind ?new-x (+ ?zero-x (nth$ 1 ?dir)))
        (bind ?new-y (+ ?zero-y (nth$ 2 ?dir)))
        (bind ?new-move (nth$ 3 ?dir))

        ;(if (and (inbound ?new-x ?new-y ?size) (new-rule ?new-x ?new-y ?state))
        (if (inbound ?new-x ?new-y ?size)
            then
                (bind ?new-pos (+ 1 (* ?new-y ?size) ?new-x))
                (bind ?new-state (swap-positions ?state ?zero-pos ?new-pos))
                (if (not (already-visited ?new-state ?visited))
                    then (bind ?neighbors (insert$ ?neighbors (+ 1 (length$ ?neighbors)) ?new-state))
                         (bind ?neighbors (insert$ ?neighbors (+ 1 (length$ ?neighbors)) ?new-move)))))

    (return ?neighbors))


(deffunction reversee (?path ?size)
     (bind ?size-visited (nth$ 1 ?path))
    (bind ?path (dequeue ?path 1))

    (bind ?size-moves (nth$ 1 ?path))
    (bind ?path (dequeue ?path 1))

    (bind ?visited (front ?path ?size-visited))
    (bind ?path (dequeue ?path ?size-visited))

    (bind ?moves (front ?path ?size-moves))
    (bind ?path (dequeue ?path ?size-moves))

    (bind ?pathing (create$))
    (bind ?move (nth$ (length$ ?moves) ?moves))
    (bind ?moves (dedequeue ?moves 1))
    (bind ?veisited (dedequeue ?visited ?size))
    (bind ?pathing (enqueue ?pathing ?move))

    (if (eq ?move nothing)
            then (return ?pathing))

    (bind ?oposite-move (create$))
    (bind ?oposite-move (find-back-move (final-state ?size) ?move))
    (bind ?state (front ?oposite-move ?size))
    (bind ?contor -1)

    (while (> (length$ ?moves) 0)
        (bind ?contor (find-contor ?state ?visited))
        (bind ?move (nth$ ?contor ?moves))
        (bind ?moves (dedequeue ?moves 1))
        (bind ?visited (remove-que ?visited ?state))
        (bind ?pathing (enqueue ?pathing ?move))

        (if (eq ?move nothing)
            then (return ?pathing))

        (bind ?oposite-move (find-back-move ?state ?move))
        (bind ?state (front ?oposite-move ?size)))

    (return FALSE))


(deffunction bfs (?board)
    (bind ?result (create$))
    (bind ?size (length$ ?board))
    (bind ?queue (create$ ?board nothing))
    (bind ?visited (create$))
    (bind ?moves (create$))

    (while (> (length$ ?queue) 0)
        (bind ?current (front ?queue ?size))
        (bind ?queue (dequeue ?queue ?size))
        (bind ?current-move (front ?queue 1))
        (bind ?queue (dequeue ?queue 1))
        (bind ?moves (insert$ ?moves (+ 1 (length$ ?moves)) ?current-move))

        (if (is-final-state ?current)
            then (bind ?visited (enqueue ?visited ?current))
                 (bind ?result (enqueue ?result (length$ ?visited)))
                 (bind ?result (enqueue ?result (length$ ?moves)))
                 (bind ?result (enqueue ?result ?visited))
                 (bind ?result (enqueue ?result ?moves))
                 (return ?result))

        (bind ?visited (insert$ ?visited (+ 1 (length$ ?visited)) ?current))
        (bind ?neighbors (generate-neighbors ?current ?visited))
        (bind ?queue (enqueue ?queue ?neighbors)))
   
    (return FALSE))


(deffunction solv-board (?board)
    (bind ?size (length$ ?board))

    (if (is-final-state ?board)
        then (printout output "Puzzle-ul este deja rezolvat!" crlf)
             (return TRUE))

    (bind ?bfs (bfs ?board))
    (bind ?path (reversee ?bfs ?size))

    (printout output "Pathul: ")
    (while (> (length$ ?path) 0)
        (bind ?mov (back ?path 1))
        (bind ?path (dedequeue ?path 1))
        (printout output "" ?mov))
    (printout output "" crlf)
    (return TRUE))


(defrule initialize-board
    =>
    (bind ?fisier-output "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\output.txt")
    (open ?fisier-output output "w")

    (bind ?fisier-input-size "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-size.txt")
    (open ?fisier-input-size input1 "r")

    (bind ?fisier-input-board "C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt")
    (open ?fisier-input-board input2 "r")

    (bind ?size (read input1))
    (bind ?size-board (* ?size ?size))
    (printout output "Size este: " ?size crlf)

    (bind ?board (take-board input2))
    (printout output "Board este: " ?board crlf)
    (assert (board ?board))

    (bind ?ok1 (check-board ?board))
    (if (eq ?ok1 FALSE)
        then (close output)
             (close input1)
             (close input2)
             (return FALSE))

    (bind ?ok2 (is-solvable ?board))
    (if (eq ?ok2 FALSE)
        then (printout output "Tabla nu este rezolvabila!" crlf)
             (close output)
             (close input1)
             (close input2)
             (return FALSE))

    (printout output "Tabla este rezolvabila!" crlf)
    (bind ?result (solv-board ?board))
    (if (eq ?result TRUE)
        then (printout output "Solutia a fost gasita!" crlf)
             (close output)
             (close input1)
             (close input2)
             (return TRUE))

    (printout output "Nu s-a gasit o solutie!" crlf)
    (close output)
    (close input1)
    (close input2)
    (return FALSE)
)
_yelper_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _YELPER_COMPLETE=complete $1 ) )
    return 0
}

complete -F _yelper_completion -o default yelper;

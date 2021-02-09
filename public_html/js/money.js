export function money_to_int(value) {
    return Math.round(Number(value) * 100)
}

export function int_to_money(value) {
    return (value / 100).toFixed(2)
}

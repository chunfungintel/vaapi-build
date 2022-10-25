package utils

import (
	"encoding/json"
	"strings"
)

const NullStr = "null"

func TrimSpace(s string) string {
	return strings.Trim(strings.TrimSpace(s), "\"")
}

func IsEmpty(s string) bool {
	return len(TrimSpace(s)) == 0
}

func IsEmptyWithValue(s string) (string, bool) {
	v := TrimSpace(s)
	if len(v) == 0 {
		return v, true
	}
	return v, false
}

func WithDefault(s, def string) string {
	v := TrimSpace(s)
	if len(v) == 0 {
		return def
	}
	return v
}

// notSet := `{}`               <Set:false> <Valid:false>
// setNull := `{"value": null}` <Set:true> <Valid:false>
// setValid := `{"value": 123}` <Set:true> <Valid:true>

func IsSet(r json.RawMessage) bool {
	return len(r) != 0
}

func IsValid(r json.RawMessage) bool {
	if IsSet(r) && string(r) != NullStr {
		return true
	}
	return false
}

func ToString(r json.RawMessage) string {
	if IsSet(r) {
		return TrimSpace(string(r))
	}
	return ""
}

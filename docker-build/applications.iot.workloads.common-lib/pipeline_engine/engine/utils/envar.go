package utils

import (
	"os"
	"strings"
)

func EnvarMap() map[string]string {
	envars := make(map[string]string)
	for _, e := range os.Environ() {
		pair := strings.SplitN(e, "=", 2)
		if len(pair) == 2 {
			envars[pair[0]] = pair[1]
		}
	}
	return envars
}

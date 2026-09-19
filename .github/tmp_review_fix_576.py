from pathlib import Path

telemetry_test = Path("openfeature/telemetry/telemetry_test.go")
text = telemetry_test.read_text()

marker = "func TestCreateEvaluationEvent_1_4_8_WithErrors(t *testing.T) {\n"
assert text.count(marker) == 1, "expected insertion marker exactly once"

block = r'''// TestCreateEvaluationEvent_1_4_14_ContextID verifies context ID precedence,
// fallback, invalid metadata handling, and omission.
func TestCreateEvaluationEvent_1_4_14_ContextID(t *testing.T) {
	tests := []struct {
		name          string
		targetingKey  string
		flagMetadata  openfeature.FlagMetadata
		wantContextID string
		wantAttribute bool
	}{
		{
			name:         "metadata takes precedence",
			targetingKey: "targeting-context",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: "metadata-context",
			},
			wantContextID: "metadata-context",
			wantAttribute: true,
		},
		{
			name:         "metadata works without targeting key",
			targetingKey: "",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: "metadata-context",
			},
			wantContextID: "metadata-context",
			wantAttribute: true,
		},
		{
			name:          "targeting key is used as fallback",
			targetingKey:  "targeting-context",
			flagMetadata:  openfeature.FlagMetadata{},
			wantContextID: "targeting-context",
			wantAttribute: true,
		},
		{
			name:         "empty metadata context uses targeting key fallback",
			targetingKey: "targeting-context",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: "",
			},
			wantContextID: "targeting-context",
			wantAttribute: true,
		},
		{
			name:         "nil metadata context uses targeting key fallback",
			targetingKey: "targeting-context",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: nil,
			},
			wantContextID: "targeting-context",
			wantAttribute: true,
		},
		{
			name:         "non-string metadata context uses targeting key fallback",
			targetingKey: "targeting-context",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: true,
			},
			wantContextID: "targeting-context",
			wantAttribute: true,
		},
		{
			name:          "context attribute is omitted when unavailable",
			targetingKey:  "",
			flagMetadata:  openfeature.FlagMetadata{},
			wantAttribute: false,
		},
		{
			name:         "invalid metadata is omitted without targeting key",
			targetingKey: "",
			flagMetadata: openfeature.FlagMetadata{
				flagMetaContextIDKey: nil,
			},
			wantAttribute: false,
		},
	}

	for _, testCase := range tests {
		t.Run(testCase.name, func(t *testing.T) {
			flagKey := "test-flag"
			providerMetadata := openfeature.Metadata{Name: "test-provider"}
			clientMetadata := openfeature.NewClientMetadata("test-client")
			evaluationContext := openfeature.NewEvaluationContext(
				testCase.targetingKey, map[string]any{},
			)
			hookContext := openfeature.NewHookContext(
				flagKey, openfeature.Boolean, true, clientMetadata,
				providerMetadata, evaluationContext,
			)
			details := openfeature.InterfaceEvaluationDetails{
				Value: true,
				EvaluationDetails: openfeature.EvaluationDetails{
					FlagKey:  flagKey,
					FlagType: openfeature.Boolean,
					ResolutionDetail: openfeature.ResolutionDetail{
						FlagMetadata: testCase.flagMetadata,
					},
				},
			}

			event := CreateEvaluationEvent(hookContext, details)
			gotContextID, ok := event.Attributes[ContextIDKey]

			if ok != testCase.wantAttribute {
				t.Fatalf(
					"context ID attribute presence = %v, want %v",
					ok, testCase.wantAttribute,
				)
			}
			if testCase.wantAttribute &&
				gotContextID != testCase.wantContextID {

				t.Errorf(
					"context ID = %v, want %q", gotContextID,
					testCase.wantContextID,
				)
			}
		})
	}
}

'''

telemetry_test.write_text(text.replace(marker, block + marker, 1))
Path("openfeature/telemetry/telemetry_context_id_test.go").unlink()

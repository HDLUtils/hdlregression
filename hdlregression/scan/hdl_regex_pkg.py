#
# Copyright (c) 2022 by HDLRegression Authors.  All rights reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at https://opensource.org/licenses/MIT.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
# HDLRegression AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER DEALINGS IN HDLRegression.
#


import re

# --------------------------------------------------------------
#  Simulator regular expressions
# --------------------------------------------------------------

# ID_SIMULATOR_WARNING = r'(?:\*\* Warning:|WARNING:|warn:)\s?(.*)'
# RE_SIMULATOR_WARNING = re.compile(ID_SIMULATOR_WARNING, flags=re.IGNORECASE)
#
# ID_SIMULATOR_ERROR = r'(?:\*\* (?:Error|Fatal): \(File: (.*), Line: (\d+)\)|ERROR:|error:|FATAL:|fatal:)\s?(.*)'
# RE_SIMULATOR_ERROR = re.compile(ID_SIMULATOR_ERROR, flags=re.IGNORECASE)

ID_RIVIERA_ERROR = r"# \*\* Error: .*"
RE_RIVIERA_ERROR = re.compile(ID_RIVIERA_ERROR, flags=re.IGNORECASE)

ID_RIVIERA_WARNING = r"# \*\* Warning: .*"
RE_RIVIERA_WARNING = re.compile(ID_RIVIERA_WARNING, flags=re.IGNORECASE)

ID_ACTIVE_HDL_ERROR = r"# \*\* Error: .*"
RE_ACTIVE_HDL_ERROR = re.compile(ID_ACTIVE_HDL_ERROR, flags=re.IGNORECASE)

ID_ACTIVE_HDL_WARNING = r"# \*\* Warning: .*"
RE_ACTIVE_HDL_WARNING = re.compile(ID_ACTIVE_HDL_WARNING, flags=re.IGNORECASE)


ID_MODELSIM_ERROR = r"[\r\n\s]?\*\*\s*(error|fatal)[\s+]?[:]?"
RE_MODELSIM_ERROR = re.compile(ID_MODELSIM_ERROR, flags=re.IGNORECASE)

ID_MODELSIM_WARNING = r"[\r\n\s]?\*\*\s*Warning[\s+]?[:]?"
RE_MODELSIM_WARNING = re.compile(ID_MODELSIM_WARNING, flags=re.IGNORECASE)

ID_NVC_ERROR = r"(error: (.*):(\d+):(\d+):\s(.*))"
RE_NVC_ERROR = re.compile(ID_NVC_ERROR, flags=re.IGNORECASE)
ID_NVC_WARNING = r"(warning: (.*):(\d+):(\d+):\s(.*))"
RE_NVC_WARNING = re.compile(ID_NVC_WARNING, flags=re.IGNORECASE)

ID_GHDL_ERROR = r"(error: (.*):(\d+):(\d+):\s(.*))"
RE_GHDL_ERROR = re.compile(ID_GHDL_ERROR, flags=re.IGNORECASE)
ID_GHDL_WARNING = r"(warning: (.*):(\d+):(\d+):\s(.*))"
RE_GHDL_WARNING = re.compile(ID_GHDL_WARNING, flags=re.IGNORECASE)

# Regex for detecting Xsim errors
ID_VIVADO_ERROR = r"[\r\n\s]?ERROR[:\s]"
RE_VIVADO_ERROR = re.compile(ID_VIVADO_ERROR, flags=re.IGNORECASE)

# Regex for detecting Xsim warnings
ID_VIVADO_WARNING = r"[\r\n\s]?WARNING[:\s]"
RE_VIVADO_WARNING = re.compile(ID_VIVADO_WARNING, flags=re.IGNORECASE)

# --------------------------------------------------------------
#  VHDL regular expressions
# --------------------------------------------------------------

ID_VHDL_TB = r"--\s*?hdlregression\s*?:\s*?tb[\s\r\n]?"
RE_VHDL_TB = re.compile(ID_VHDL_TB, flags=re.IGNORECASE)

ID_VHDL_LIBRARY = r"\blibrary\s+.*;"  # r'[\s*]?library\s+.*;'
RE_VHDL_LIBRARY = re.compile(ID_VHDL_LIBRARY, flags=re.IGNORECASE)

#  ID_VHDL_USE = r'[\s+]?use\s+.*;'
ID_VHDL_USE = r"(^|\W)use\s+.*"
RE_VHDL_USE = re.compile(ID_VHDL_USE, flags=re.IGNORECASE)

ID_VHDL_USE_CONTEXT = r"[\s+]?context\s+.*;"
RE_VHDL_USE_CONTEXT = re.compile(ID_VHDL_USE_CONTEXT, flags=re.IGNORECASE)

ID_VHDL_ENTITY = r".*[\r\n\s]?entity\s"
RE_VHDL_ENTITY = re.compile(ID_VHDL_ENTITY, flags=re.IGNORECASE)

ID_VHDL_ENTITY_DECLARATION = r"[\s+]?entity\s+.*\s+[\s\r\n]?is"
RE_VHDL_ENTITY_DECLARATION = re.compile(ID_VHDL_ENTITY_DECLARATION, flags=re.IGNORECASE)

ID_VHDL_CONFIGURATION_INSTANTIATION = r"\s+.*:\s+configuration\s+\w+"
RE_VHDL_CONFIGURATION_INSTANTIATION = re.compile(ID_VHDL_CONFIGURATION_INSTANTIATION, flags=re.IGNORECASE)

ID_VHDL_CONFIGURATION_DECLARATION = r"[\s+]?configuration\s+.*\s+[\s\r\n]?of\s+.*\s+is"
RE_VHDL_CONFIGURATION_DECLARATION = re.compile(ID_VHDL_CONFIGURATION_DECLARATION, flags=re.IGNORECASE)

ID_VHDL_COMPONENT = r"\bcomponent\s+[is]?"
RE_VHDL_COMPONENT = re.compile(ID_VHDL_COMPONENT, flags=re.IGNORECASE)

ID_VHDL_PACKAGE = r"(^|\W)package(?!\s+body)\s+.*is(?!\s+new)"
RE_VHDL_PACKAGE = re.compile(ID_VHDL_PACKAGE, flags=re.IGNORECASE)

ID_VHDL_NEW_PACKAGE = r"[\s+]?package\s+.*\s+is\s+new\s+"  # (^|\W)
RE_VHDL_NEW_PACKAGE = re.compile(ID_VHDL_NEW_PACKAGE, flags=re.IGNORECASE)

ID_VHDL_ARCHITECTURE = r"[\s\r\n]?(architecture).*\s+of\s+"
RE_VHDL_ARCHITECTURE = re.compile(ID_VHDL_ARCHITECTURE, flags=re.IGNORECASE)

ID_VHDL_CONTEXT = r"[\s+]?context\s+[\s\r\n]?.*\s+[\s\r\n]?is"
RE_VHDL_CONTEXT = re.compile(ID_VHDL_CONTEXT, flags=re.IGNORECASE)

ID_VHDL_GENERIC = r"\s*generic\s*[\s\r\n]?[(]"
RE_VHDL_GENERIC = re.compile(ID_VHDL_GENERIC, flags=re.IGNORECASE)

ID_VHDL_SEMI_COLON = r"[\s+]?;[\s\r\n]?"
RE_VHDL_SEMI_COLON = re.compile(ID_VHDL_SEMI_COLON, flags=re.IGNORECASE)

ID_VHDL_FOR_STATEMENT = r"(^|\W)for\s+"
RE_VHDL_FOR_STATEMENT = re.compile(ID_VHDL_FOR_STATEMENT, flags=re.IGNORECASE)

ID_VHDL_IS_REFERENCE = r".*\s+is\s+\w+\."
RE_VHDL_IS_REFERENCE = re.compile(ID_VHDL_IS_REFERENCE, flags=re.IGNORECASE)

ID_VHDL_ATTRIBUTE = r"\battribute\b"
RE_VHDL_ATTRIBUTE = re.compile(ID_VHDL_ATTRIBUTE, flags=re.IGNORECASE)

ID_VHDL_END = r"[\s\r\n]?\bend\s*.*;"  # r'[\s\r\n]?end\s*;'
RE_VHDL_END = re.compile(ID_VHDL_END, flags=re.IGNORECASE)

ID_VHDL_END_ARCH = (r"\bend\s*(;|architecture\s*(;|\w+\s*;))")
RE_VHDL_END_ARCH = re.compile(ID_VHDL_END_ARCH, flags=re.IGNORECASE)

ID_VHDL_END_PKG = (r"\bend\s*(;|package\s*(;|\w+\s*;))")
RE_VHDL_END_PKG = re.compile(ID_VHDL_END_PKG, flags=re.IGNORECASE)

ID_VHDL_END_PKG_BODY = r"\bend\s*(;|package[\s+]body\s*(;|\w+\s*;))"
RE_VHDL_END_PKG_BODY = re.compile(ID_VHDL_END_PKG_BODY, flags=re.IGNORECASE)

ID_VHDL_END_CONTEXT = (r"\bend\s*(;|context\s*(;|\w+\s*;))")
RE_VHDL_END_CONTEXT = re.compile(ID_VHDL_END_CONTEXT, flags=re.IGNORECASE)

ID_VHDL_COMMENT_BLOCK_START = r"\/\*"
RE_VHDL_COMMENT_BLOCK_START = re.compile(ID_VHDL_COMMENT_BLOCK_START, flags=re.IGNORECASE)

#  ID_VHDL_COMMENT_BLOCK_START_LINE = r'.*' + ID_VHDL_COMMENT_BLOCK_START
#  RE_VHDL_COMMENT_BLOCK_START_LINE = re.compile(ID_VHDL_COMMENT_BLOCK_START_LINE, flags=re.IGNORECASE)

ID_VHDL_COMMENT_BLOCK_START_LINE = ID_VHDL_COMMENT_BLOCK_START + r".*"
RE_VHDL_COMMENT_BLOCK_START_LINE = re.compile(ID_VHDL_COMMENT_BLOCK_START_LINE, flags=re.IGNORECASE)

ID_VHDL_COMMENT_BLOCK_END = r"\*\/"
RE_VHDL_COMMENT_BLOCK_END = re.compile(ID_VHDL_COMMENT_BLOCK_END, flags=re.IGNORECASE)

#  ID_VHDL_COMMENT_BLOCK_END_LINE = ID_VHDL_COMMENT_BLOCK_END + r'.*'
ID_VHDL_COMMENT_BLOCK_END_LINE = r".*" + ID_VHDL_COMMENT_BLOCK_END
RE_VHDL_COMMENT_BLOCK_END_LINE = re.compile(ID_VHDL_COMMENT_BLOCK_END_LINE, flags=re.IGNORECASE)

ID_VHDL_COMMENT = r"--"
RE_VHDL_COMMENT = re.compile(ID_VHDL_COMMENT, flags=re.IGNORECASE)

ID_VHDL_COMMENT_LINE = ID_VHDL_COMMENT + r".*"
RE_VHDL_COMMENT_LINE = re.compile(ID_VHDL_COMMENT_LINE, flags=re.IGNORECASE)

ID_VHDL_RESERVED = [
    "abs",
    "configuration",
    "impure",
    "null",
    "rem",
    "type",
    "access",
    "constant",
    "in",
    "of",
    "report",
    "unaffected",
    "after",
    "disconnect",
    "inertial",
    "on",
    "return",
    "units",
    "alias",
    "downto",
    "inout",
    "open",
    "rol",
    "until",
    "all",
    "else",
    "is",
    "or",
    "ror",
    "use",
    "and",
    "elsif",
    "label",
    "others",
    "select",
    "variable",
    "architecture",
    "end",
    "library",
    "out",
    "severity",
    "wait",
    "array",
    "entity",
    "linkage",
    "package",
    "signal",
    "when",
    "assert",
    "exit",
    "literal",
    "port",
    "shared",
    "while",
    "attribute",
    "file",
    "loop",
    "postponed",
    "sla",
    "with",
    "begin",
    "for",
    "map",
    "procedure",
    "sll",
    "xnor",
    "block",
    "function",
    "mod",
    "process",
    "sra",
    "xor",
    "body",
    "generate",
    "nand",
    "pure",
    "srl",
    "buffer",
    "generic",
    "new",
    "range",
    "subtype",
    "bus",
    "group",
    "next",
    "record",
    "then",
    "case",
    "guarded",
    "nor",
    "register",
    "to",
    "component",
    "if",
    "not",
    "reject",
    "transport",
]
RE_VHDL_RESERVED = re.compile(r"\b(?:%s)\b" % "|".join(ID_VHDL_RESERVED))

# --------------------------------------------------------------
#  Verilog regular expressions
# --------------------------------------------------------------

ID_VERILOG_SEMI_COLON = r"[\s+]?;[\s\r\n]?"
RE_VERILOG_SEMI_COLON = re.compile(ID_VERILOG_SEMI_COLON, flags=re.IGNORECASE)

ID_VERILOG_PARANTECE_START = r"[\s+]?\([\s\r\n]?"
RE_VERILOG_PARANTECE_START = re.compile(ID_VERILOG_PARANTECE_START, flags=re.IGNORECASE)

ID_VERILOG_PARANTECE_END = r"[\s+]?\)[\s\r\n]?"
RE_VERILOG_PARANTECE_END = re.compile(ID_VERILOG_PARANTECE_END, flags=re.IGNORECASE)

ID_VERILOG_TB = r"//\s*hdlregression\s*:\s*tb[\s\r\n]?"
RE_VERILOG_TB = re.compile(ID_VERILOG_TB, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)

ID_VERILOG_MODULE = r"\bmodule\s+.*"  # [\s+]?module\s+
RE_VERILOG_MODULE = re.compile(ID_VERILOG_MODULE, flags=re.IGNORECASE)

ID_VERILOG_MACRO_MODULE = r"\bmacromodule\s+.*"  # [\s+]?module\s+
RE_VERILOG_MACRO_MODULE = re.compile(ID_VERILOG_MACRO_MODULE, flags=re.IGNORECASE)

#  ID_VERILOG_MODULE_DECLARATION = r'\bmodule\s+.*\s+[\s\r\n]?'  # r'[\s+]?module\s+.*\s+[\s\r\n]?'
#  RE_VERILOG_MODULE_DECLARATION = re.compile(ID_VERILOG_MODULE_DECLARATION, flags=re.IGNORECASE)

ID_VERILOG_MODULE_END = r"\bendmodule\s+.*"
RE_VERILOG_MODULE_END = re.compile(ID_VERILOG_MODULE_END, flags=re.IGNORECASE)

ID_VERILOG_LEGAL_START_UNDERSC = r"[\s+]?\_+\w+"
RE_VERILOG_LEGAL_START_UNDERSC = re.compile(ID_VERILOG_LEGAL_START_UNDERSC, flags=re.IGNORECASE)

ID_VERILOG_LEGAL_START_WORD = r"[\s+]?[a-zA-Z]+\w*"
RE_VERILOG_LAGEL_START_WORD = re.compile(ID_VERILOG_LEGAL_START_WORD, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_BLOCK_START = r"\/\*"
RE_VERILOG_COMMENT_BLOCK_START = re.compile(ID_VERILOG_COMMENT_BLOCK_START, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_BLOCK_START_LINE = ID_VERILOG_COMMENT_BLOCK_START + r".*"
RE_VERILOG_COMMENT_BLOCK_START_LINE = re.compile(ID_VERILOG_COMMENT_BLOCK_START_LINE, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_BLOCK_END = r"\*\/"
RE_VERILOG_COMMENT_BLOCK_END = re.compile(ID_VERILOG_COMMENT_BLOCK_END, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_BLOCK_END_LINE = r".*" + ID_VERILOG_COMMENT_BLOCK_END
RE_VERILOG_COMMENT_BLOCK_END_LINE = re.compile(ID_VERILOG_COMMENT_BLOCK_END_LINE, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_BLOCK = (ID_VERILOG_COMMENT_BLOCK_START + r".*" + ID_VERILOG_COMMENT_BLOCK_END)
RE_VERILOG_COMMENT_BLOCK = re.compile(ID_VERILOG_COMMENT_BLOCK, flags=re.IGNORECASE)

ID_VERILOG_COMMENT = r"//"
RE_VERILOG_COMMENT = re.compile(ID_VERILOG_COMMENT, flags=re.IGNORECASE)

ID_VERILOG_COMMENT_LINE = ID_VERILOG_COMMENT + ".*"
RE_VERILOG_COMMENT_LINE = re.compile(ID_VERILOG_COMMENT_LINE, flags=re.IGNORECASE)

ID_VERILOG_RESERVED = [
    "always",
    "end",
    "ifnone",
    "or",
    "rpmos",
    "tranif1",
    "and",
    "endcase",
    "initial",
    "output",
    "rtran",
    "tri",
    "assign",
    "endmodule",
    "inout",
    "parameter",
    "rtranif0",
    "tri0",
    "begin",
    "endfunction",
    "input",
    "pmos",
    "rtranif1",
    "tri1",
    "buf",
    "endprimitive",
    "integer",
    "posedge",
    "scalared",
    "triand",
    "bufif0",
    "endspecify",
    "join",
    "primitive",
    "small",
    "trior",
    "bufif1",
    "endtable",
    "large",
    "pull0",
    "specify",
    "trireg",
    "case",
    "endtask",
    "macromodule",
    "pull1",
    "specparam",
    "vectored",
    "casex",
    "event",
    "medium",
    "pullup",
    "strong0",
    "wait",
    "casez",
    "for",
    "module",
    "pulldown",
    "strong1",
    "wand",
    "cmos",
    "force",
    "nand",
    "rcmos",
    "supply0",
    "weak0",
    "deassign",
    "forever",
    "negedge",
    "real",
    "supply1",
    "weak1",
    "default",
    "for",
    "nmos",
    "realtime",
    "table",
    "while",
    "defparam",
    "function",
    "nor",
    "reg",
    "task",
    "wire",
    "disable",
    "highz0",
    "not",
    "release",
    "time",
    "wor",
    "edge",
    "highz1",
    "notif0",
    "repeat",
    "tran",
    "xnor",
    "else",
    "if",
    "notif1",
    "rnmos",
    "tranif0",
    "xor",
]
RE_VERILOG_RESERVED = re.compile(r"\b(?:%s)\b" % "|".join(ID_VERILOG_RESERVED))


# --------------------------------------------------------------
#  Tool box
# --------------------------------------------------------------

ID_ASSERTION = r"\bassert\s+.+\s+report\s+.+\s+severity\s+\w+\s*;"
RE_ASSERTION = re.compile(ID_ASSERTION, flags=re.IGNORECASE)

ID_NOTE_ASSERTION = r"\bassert\s+.+\s+report\s+.+\s+severity\s+note\s*;"
RE_NOTE_ASSERTION = re.compile(ID_NOTE_ASSERTION, flags=re.IGNORECASE)

ID_WARNING_ASSERTION = r"\bassert\s+.+\s+report\s+.+\s+severity\s+warning\s*;"
RE_WARNING_ASSERTION = re.compile(ID_WARNING_ASSERTION, flags=re.IGNORECASE)

ID_ERROR_ASSERTION = r"\bassert\s+.+\s+report\s+.+\s+severity\s+error\s*;"
RE_ERROR_ASSERTION = re.compile(ID_ERROR_ASSERTION, flags=re.IGNORECASE)

ID_FAILURE_ASSERTION = r"\bassert\s+.+\s+report\s+.+\s+severity\s+failure\s*;"
RE_FAILURE_ASSERTION = re.compile(ID_FAILURE_ASSERTION, flags=re.IGNORECASE)

-- =======================================================================================
--   This Sail RISC-V architecture model, comprising all files and
--   directories except where otherwise noted is subject the BSD
--   two-clause license in the LICENSE file.
--
--   SPDX-License-Identifier: BSD-2-Clause
-- =======================================================================================

import Sail.Sail
import LeanIM.Defs
import LeanIM.Gmp

open Sail
open ConcurrencyInterfaceV1
open LeanIM

def print_bits (_ : String) (_ : BitVec n) : Unit := ()
def print_string (_ : String) (_ : String) : Unit := ()
def prerr_string (_: String) : Unit := ()
def putchar {T} (_: T ) : Unit := ()
def string_of_int (z : Int) := s!"{z}"

section defs

variable [Arch]

-- Platform definitions
section Effectful

variable {Register : Type} {RegisterType : Register → Type} [DecidableEq Register] [Hashable Register]

axiom plat_term_write {α} : α → SailM Unit
axiom plat_term_read : Unit → SailM String

-- Reservations
axiom load_reservation : Arch.pa → Nat → SailM Unit
axiom match_reservation : Arch.pa → Bool
axiom cancel_reservation : Unit → SailM Unit
axiom valid_reservation : Unit → Bool

axiom get_16_random_bits : Unit → SailM (BitVec 16)
axiom sys_enable_experimental_extensions : Unit → Bool

end Effectful

-- Floats

-- Termination of currentlyEnabled
instance : SizeOf extension where
  sizeOf := extension.ctorIdx

macro_rules | `(tactic| decreasing_trivial) => `(tactic| decide)

'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogTrigger,
} from './ui/dialog'
import { Button } from 'C:/Users/berky/oxide/src/components/ui/button'


const UploadButton = ({
  isSubscribed,
}: {
  isSubscribed: boolean
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false)

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(v) => {
        if (!v) {
          setIsOpen(v)
        }
      }}>
      <DialogTrigger
        onClick={() => setIsOpen(true)}
        asChild>
        <Button>Upload the file</Button>
      </DialogTrigger>
    </Dialog>
  )
}

export default UploadButton